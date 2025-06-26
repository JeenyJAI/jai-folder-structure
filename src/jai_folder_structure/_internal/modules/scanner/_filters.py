"""Filtering functionality for scanner module."""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from fnmatch import translate as fnmatch_translate

from .._utils import batch_replace, get_relative_path


class GitignoreFilter:
    """Parser and matcher for .gitignore files."""
    
    def __init__(self, allow_patterns: Optional[List[str]] = None) -> None:
        self.patterns: List[Tuple[re.Pattern, bool, str]] = []
        self._cache: dict[Path, bool] = {}
        self.allow_patterns = allow_patterns or []
    
    def load_gitignore(self, gitignore_path: Path) -> None:
        """Load patterns from .gitignore file."""
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if self._should_skip_pattern(line):
                continue
            
            negation = False
            if line.startswith('!'):
                negation = True
                line = line[1:]
            
            pattern = self._gitignore_to_regex(line)
            if pattern:
                self.patterns.append((pattern, negation, line))
    
    def _should_skip_pattern(self, gitignore_pattern: str) -> bool:
        """Check if pattern should be skipped due to allow list."""
        pattern_to_check = gitignore_pattern.rstrip('/')
        
        for allow in self.allow_patterns:
            allow = allow.strip()
            
            if pattern_to_check == allow:
                return True
            
            # Check if allow pattern would match the gitignore pattern
            if '*' in allow or '?' in allow:
                allow_regex = fnmatch_translate(allow)
                if re.match(allow_regex, pattern_to_check):
                    return True
        
        return False
    
    def _gitignore_to_regex(self, pattern: str) -> Optional[re.Pattern]:
        """Convert gitignore pattern to compiled regex."""
        # Handle directory-only patterns
        is_dir_only = pattern.endswith('/')
        if is_dir_only:
            pattern = pattern[:-1]
        
        # Handle absolute patterns
        is_absolute = pattern.startswith('/')
        if is_absolute:
            pattern = pattern[1:]
        
        # Use batch_replace for efficiency
        replacements = {
            '.': r'\.',
            '+': r'\+',
            '^': r'\^',
            '$': r'\$',
            '(': r'\(',
            ')': r'\)',
            '[': r'\[',
            ']': r'\]',
            '{': r'\{',
            '}': r'\}'
        }
        pattern = batch_replace(pattern, replacements)
        
        # Convert gitignore wildcards
        pattern = pattern.replace('**/', '(?:.*/)?')
        pattern = pattern.replace('**', '.*')
        pattern = pattern.replace('*', '[^/]*')
        pattern = pattern.replace('?', '[^/]')
        
        # Build final regex
        if is_absolute:
            regex = f'^{pattern}'
        else:
            regex = f'(?:^|/){pattern}'
        
        if is_dir_only:
            regex += '/$'
        else:
            regex += '(?:/|$)'
        
        try:
            return re.compile(regex)
        except re.error:
            return None
    
    def is_ignored(self, path: Path, is_dir: bool, base_path: Path) -> bool:
        """Check if path should be ignored."""
        if path in self._cache:
            return self._cache[path]
        
        rel_path = get_relative_path(path, base_path)
        if not rel_path:
            return False
        
        path_str = rel_path
        if is_dir:
            path_str += '/'
        
        ignored = False
        for pattern, negation, _ in self.patterns:
            if pattern.search(path_str):
                ignored = not negation
        
        self._cache[path] = ignored
        return ignored
    
    def clear_cache(self) -> None:
        """Clear the path cache."""
        self._cache.clear()


class PatternMatcher:
    """Pattern matcher for include/exclude patterns."""
    
    @staticmethod
    def compile_patterns(patterns: List[str]) -> List[re.Pattern]:
        """Compile glob patterns to regex patterns."""
        compiled = []
        for pattern in patterns:
            pattern = pattern.strip()
            if not pattern:
                continue
                
            regex = fnmatch_translate(pattern)
            try:
                compiled.append(re.compile(regex))
            except re.error:
                pass
        return compiled
    
    @staticmethod
    def matches_any(name: str, patterns: List[re.Pattern]) -> bool:
        """Check if name matches any pattern."""
        return any(pattern.match(name) for pattern in patterns)


def create_gitignore_filter(base_path: Path, gitignore_path: Optional[Path] = None,
                           allow_patterns: Optional[List[str]] = None) -> GitignoreFilter:
    """Create and initialize a gitignore filter."""
    filter = GitignoreFilter(allow_patterns=allow_patterns)
    
    if gitignore_path and gitignore_path.exists():
        filter.load_gitignore(gitignore_path)
    else:
        default_gitignore = base_path / '.gitignore'
        if default_gitignore.exists():
            filter.load_gitignore(default_gitignore)
    
    return filter
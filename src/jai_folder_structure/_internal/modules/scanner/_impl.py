"""Scanner implementation."""

import time
from pathlib import Path
from typing import List, Optional

from ..models.api import FileNode, Structure, is_text_file
from .._constants import DEFAULT_EXCLUSIONS
from .._utils import format_error_message
from .api import ScanOptions, ScannerProtocol
from ._filters import create_gitignore_filter, PatternMatcher


class FileSystemScanner(ScannerProtocol):
    """Implementation of file system scanner."""
    
    def scan(self, path: Path, options: ScanOptions) -> Structure:
        """Scan directory and return results."""
        start_time = time.time()
        
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        gitignore_filter = None
        if options.use_gitignore:
            gitignore_filter = create_gitignore_filter(
                path, 
                options.gitignore_path,
                allow_patterns=options.allow
            )
        
        exclusion_patterns = options.exclude_patterns.copy()
        if options.use_default_exclusions:
            exclusion_patterns.extend(DEFAULT_EXCLUSIONS)
        
        include_patterns = PatternMatcher.compile_patterns(options.include_patterns)
        exclude_patterns = PatternMatcher.compile_patterns(exclusion_patterns)
        allow_patterns = PatternMatcher.compile_patterns(options.allow)
        
        root_node = self._scan_node(
            path=path,
            base_path=path,
            options=options,
            gitignore_filter=gitignore_filter,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            allow_patterns=allow_patterns,
            depth=0
        )
        
        scan_time = time.time() - start_time
        
        return Structure(
            root=root_node,
            scan_time=scan_time,
            _scan_options=options,
            _has_details=options.detailed
        )
    
    def _scan_node(self, path: Path, base_path: Path, options: ScanOptions,
                   gitignore_filter, include_patterns: List, exclude_patterns: List,
                   allow_patterns: List, depth: int) -> FileNode:
        """Scan a single node."""
        name = path.name if path != base_path else path.name
        
        try:
            is_dir = path.is_dir()
        except (OSError, PermissionError) as e:
            return FileNode(
                name=name,
                path=path,
                is_dir=True,
                error=format_error_message(str(e))
            )
        
        node = FileNode(
            name=name,
            path=path,
            is_dir=is_dir
        )
        
        if is_dir:
            if options.max_depth is not None and depth >= options.max_depth:
                return node
            
            try:
                self._scan_directory(
                    node, base_path, options, gitignore_filter,
                    include_patterns, exclude_patterns, allow_patterns, depth
                )
            except (OSError, PermissionError) as e:
                node.error = format_error_message(str(e))
        else:
            self._scan_file(node, options)
        
        return node
    
    def _scan_directory(self, node: FileNode, base_path: Path, options: ScanOptions,
                        gitignore_filter, include_patterns: List, exclude_patterns: List,
                        allow_patterns: List, depth: int) -> None:
        """Scan directory contents."""
        try:
            entries = list(node.path.iterdir())
        except (OSError, PermissionError) as e:
            node.error = format_error_message(str(e))
            return
        
        entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        
        for entry in entries:
            if self._should_exclude(
                entry, base_path, gitignore_filter,
                include_patterns, exclude_patterns, allow_patterns
            ):
                continue
            
            child_node = self._scan_node(
                entry, base_path, options, gitignore_filter,
                include_patterns, exclude_patterns, allow_patterns,
                depth + 1
            )
            
            node.children.append(child_node)
    
    def _scan_file(self, node: FileNode, options: ScanOptions) -> None:
        """Scan file properties."""
        try:
            node.size = node.path.stat().st_size
            
            # Count lines only in detailed mode for text files
            if options.detailed and is_text_file(node.path):
                node.lines = self._count_lines(node.path)
        except (OSError, PermissionError) as e:
            node.error = format_error_message(str(e))
    
    def _should_exclude(self, path: Path, base_path: Path, gitignore_filter,
                       include_patterns: List, exclude_patterns: List, 
                       allow_patterns: List) -> bool:
        """Check if path should be excluded."""
        name = path.name
        
        try:
            is_dir = path.is_dir()
        except (OSError, PermissionError):
            return True
        
        # HIGHEST PRIORITY: allow patterns
        if allow_patterns and PatternMatcher.matches_any(name, allow_patterns):
            return False
        
        if exclude_patterns and PatternMatcher.matches_any(name, exclude_patterns):
            if include_patterns:
                return not PatternMatcher.matches_any(name, include_patterns)
            return True
        
        if include_patterns:
            if is_dir:
                return False  # Don't exclude directories
            if not PatternMatcher.matches_any(name, include_patterns):
                return True
        
        if gitignore_filter and gitignore_filter.is_ignored(path, is_dir, base_path):
            return True
        
        return False
    
    def _count_lines(self, path: Path) -> Optional[int]:
        """Count lines in a text file."""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return None
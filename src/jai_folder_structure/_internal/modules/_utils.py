"""Common utility functions for jai_folder_structure library."""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from functools import lru_cache

from ._constants import (
    WINDOWS_RESERVED_NAMES,
    WINDOWS_INVALID_CHARS,
    MIN_PRINTABLE_CHAR_CODE,
    MAX_PATH_LENGTH_WINDOWS,
    MAX_PATH_LENGTH_UNIX,
    PATH_SAFETY_MARGIN
)

# ==============================================================================
# PATH UTILITIES
# ==============================================================================

def build_path(parent_path: str, name: str, is_dir: bool = False) -> str:
    """Build path from parent and name."""
    if not parent_path:
        path = name
    else:
        path = f"{parent_path}/{name}"
    
    if is_dir and not path.endswith('/'):
        path += '/'
    
    return path


def get_relative_path(path: Path, base_path: Path) -> Optional[str]:
    """Get relative path as string, returning None if not relative."""
    try:
        rel_path = path.relative_to(base_path)
        return str(rel_path).replace('\\', '/')
    except ValueError:
        return None


def normalize_path_separators(path: str) -> str:
    """Normalize path separators to forward slashes."""
    return path.replace('\\', '/')


# ==============================================================================
# FORMATTING UTILITIES
# ==============================================================================

def calculate_padding(current_width: int, target_width: int, min_padding: int = 1) -> str:
    """Calculate padding spaces for alignment.
    
    Args:
        current_width: Current text width
        target_width: Target width for alignment
        min_padding: Minimum padding spaces
        
    Returns:
        String of spaces for padding
    """
    padding_needed = max(min_padding, target_width - current_width)
    return " " * padding_needed


@lru_cache(maxsize=128)
def format_error_message(error: str, max_length: int = 50) -> str:
    """Format error message for display.
    
    Args:
        error: Original error message
        max_length: Maximum length for error message
        
    Returns:
        Formatted error message
    """
    # Common error patterns
    error_patterns = {
        "Permission denied": "Permission denied",
        "File not found": "File not found",
        "Access is denied": "Access denied",
        "No such file or directory": "File not found",
        "Is a directory": "Is a directory",
        "Not a directory": "Not a directory",
    }
    
    # Check for known patterns
    for pattern, short_msg in error_patterns.items():
        if pattern in error:
            return short_msg
    
    # For unknown errors, truncate if too long
    if ':' in error and len(error) > max_length:
        return error.split(':')[0]
    elif len(error) > max_length:
        return error[:max_length-3] + "..."
    
    return error


def strip_tree_prefix(line: str) -> str:
    """Strip tree drawing characters from line start.
    
    Args:
        line: Line with potential tree characters
        
    Returns:
        Line without tree prefix
    """
    # Tree characters to strip
    tree_chars = {'│', '├', '└', '─', ' '}
    
    i = 0
    while i < len(line) and line[i] in tree_chars:
        i += 1
    
    return line[i:].lstrip()


# ==============================================================================
# VALIDATION UTILITIES
# ==============================================================================

def is_valid_filename(name: str, strict: bool = True) -> Tuple[bool, Optional[str]]:
    """Check if filename is valid across platforms.
    
    Args:
        name: Filename to validate
        strict: Apply Windows rules on all platforms
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Empty name"
    
    if name in ('.', '..'):
        return False, f"Invalid name '{name}'"
    
    if '\0' in name:
        return False, "Null byte in name"
    
    if '\t' in name:
        return False, "TAB character in name"
    
    if '/' in name or '\\' in name:
        return False, "Path separator in name"
    
    # Windows-specific checks (applied based on strict flag)
    if sys.platform == "win32" or strict:
        # Check reserved names
        name_upper = name.upper()
        base_name = name_upper.split('.')[0] if '.' in name_upper else name_upper
        if base_name in WINDOWS_RESERVED_NAMES:
            return False, f"Reserved Windows name '{name}'"
        
        # Check invalid characters
        for char in WINDOWS_INVALID_CHARS:
            if char in name:
                return False, f"Invalid character '{char}' in name"
        
        # Check control characters
        for char in name:
            if ord(char) < MIN_PRINTABLE_CHAR_CODE:
                return False, f"Control character (code {ord(char)}) in name"
    
    # Check length
    if len(name) > 255:
        return False, f"Name too long ({len(name)} chars)"
    
    return True, None


def validate_path_length(path: str, platform: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Validate path length for target platform.
    
    Args:
        path: Full path to validate
        platform: Target platform ('win32', 'posix', or None for current)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if platform is None:
        platform = sys.platform
    
    max_length = MAX_PATH_LENGTH_WINDOWS if platform == "win32" else MAX_PATH_LENGTH_UNIX
    actual_limit = max_length - PATH_SAFETY_MARGIN
    
    if len(path) > actual_limit:
        return False, f"Path too long ({len(path)} chars, max {actual_limit})"
    
    return True, None


def is_path_traversal_attempt(path: str) -> bool:
    """Check if path contains directory traversal attempts."""
    if ".." in path:
        return True
    
    if path.startswith("/") or path.startswith("\\"):
        return True
    
    # Check for absolute Windows paths
    if len(path) >= 2 and path[1] == ':':
        return True
    
    return False


# ==============================================================================
# COLLECTION UTILITIES
# ==============================================================================

def merge_patterns(*pattern_lists: List[str]) -> List[str]:
    """Merge multiple pattern lists, removing duplicates while preserving order.
    
    Args:
        *pattern_lists: Variable number of pattern lists
        
    Returns:
        Merged list with unique patterns
    """
    seen = set()
    result = []
    
    for patterns in pattern_lists:
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern and pattern not in seen:
                seen.add(pattern)
                result.append(pattern)
    
    return result


def group_by_extension(paths: List[Path]) -> Dict[str, List[Path]]:
    """Group paths by file extension.
    
    Args:
        paths: List of Path objects
        
    Returns:
        Dictionary mapping extensions to paths
    """
    groups: Dict[str, List[Path]] = {}
    
    for path in paths:
        if path.is_file():
            ext = path.suffix.lower()
            if ext not in groups:
                groups[ext] = []
            groups[ext].append(path)
    
    return groups


# ==============================================================================
# PERFORMANCE UTILITIES
# ==============================================================================

def batch_replace(text: str, replacements: Dict[str, str]) -> str:
    """Perform multiple string replacements efficiently.
    
    Args:
        text: Original text
        replacements: Dictionary of {old: new} replacements
        
    Returns:
        Text with all replacements applied
    """
    if not replacements:
        return text
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_items = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old, new in sorted_items:
        text = text.replace(old, new)
    
    return text


def build_string_list(items: List[str]) -> str:
    """Build string from list efficiently using join.
    
    Args:
        items: List of string items
        
    Returns:
        Combined string
    """
    return '\n'.join(items)


# ==============================================================================
# TYPE CONVERSION UTILITIES
# ==============================================================================

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    return default
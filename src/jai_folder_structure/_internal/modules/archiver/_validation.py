"""Structure validation for archiver module."""

import sys
from typing import Dict, Any, List, Tuple, Set

from .._constants import MAX_NESTING_DEPTH
from .._utils import (
    is_valid_filename,
    validate_path_length,
    is_path_traversal_attempt,
    build_path
)


def validate_structure(structure: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate file/directory structure."""
    errors = []
    
    if not structure:
        return True, []
    
    _validate_level(structure, "", 0, set(), errors)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def _validate_level(structure: Dict[str, Any], current_path: str, 
                   depth: int, seen_paths: Set[str], errors: List[str]) -> None:
    """Validate single level of structure recursively."""
    if depth > MAX_NESTING_DEPTH:
        errors.append(f"Maximum nesting depth exceeded at: {current_path}")
        return
    
    level_names: Set[str] = set()
    
    for name, content in structure.items():
        # Validate filename
        is_valid, error_msg = is_valid_filename(name, strict=True)
        if not is_valid:
            errors.append(f"{error_msg} at: {current_path or 'root'}")
            continue
        
        if sys.platform == "win32" or True:  # strict mode always checks Windows rules
            if name.endswith('.') or name.endswith(' '):
                errors.append(f"Windows doesn't allow names ending with dot or space: '{name}' at: {current_path or 'root'}")
                continue
        
        # Check for duplicates (case-insensitive on Windows)
        name_key = name.lower() if sys.platform == "win32" else name
        if name_key in level_names:
            errors.append(f"Duplicate name '{name}' in: {current_path or 'root'}")
        level_names.add(name_key)
        
        # Build full path
        full_path = build_path(current_path, name)
        
        # Security check
        if is_path_traversal_attempt(name):
            errors.append(f"Security error: path traversal attempt detected in '{name}'")
            continue
        
        # Path length validation
        is_valid, error_msg = validate_path_length(full_path)
        if not is_valid:
            errors.append(f"{error_msg} at: {current_path or 'root'}")
        
        # Check for duplicate paths
        if full_path in seen_paths:
            errors.append(f"Duplicate path: {full_path}")
        seen_paths.add(full_path)
        
        # Recurse for directories
        if isinstance(content, dict):
            _validate_level(content, full_path, depth + 1, seen_paths, errors)
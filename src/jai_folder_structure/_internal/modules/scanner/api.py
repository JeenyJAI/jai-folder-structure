"""Scanner module interface."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, List, Optional

from ..models.api import FileNode, Structure
from .._constants import DEFAULT_EXCLUSIONS


@dataclass
class ScanOptions:
    """Options for directory scanning. Internal use only."""
    
    detailed: bool = False
    use_gitignore: bool = False
    use_default_exclusions: bool = False
    gitignore_path: Optional[Path] = None
    include_patterns: List[str] = field(default_factory=list)  # e.g., "*.py"
    exclude_patterns: List[str] = field(default_factory=list)  # e.g., "*.tmp"
    allow: List[str] = field(default_factory=list)  # highest priority
    max_depth: Optional[int] = None


class ScannerProtocol(Protocol):
    """Protocol for directory scanners. Internal use only."""
    
    def scan(self, path: Path, options: ScanOptions) -> Structure:
        """Scan directory and return results.
        
        Args:
            path: Directory path to scan
            options: Scanning options
            
        Returns:
            Structure with file tree and statistics
        """
        ...


def create_scanner() -> ScannerProtocol:
    """Create a file system scanner instance. Internal use only.
    
    Returns:
        Scanner implementation
    """
    from ._impl import FileSystemScanner
    return FileSystemScanner()


def get_structure(
    path: str | Path,
    *,
    use_gitignore: bool = False,
    use_default_exclusions: bool = False,
    gitignore_path: Optional[str | Path] = None,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    allow: Optional[List[str]] = None
) -> Structure:
    """Get directory structure with specified options.
    
    High-level function for analyzing directories. Performs fast scan by default.
    Use to_string() or to_file() with detailed=True for full information.
    
    Args:
        path: Directory path to analyze
        use_gitignore: Use .gitignore files for filtering
        use_default_exclusions: Use default exclusion patterns
        gitignore_path: Path to specific .gitignore file
        include_patterns: File patterns to include (wildcards: * and ?)
        exclude_patterns: File patterns to exclude (wildcards: * and ?)
        allow: Patterns to always allow (overrides all exclusions)
        
    Returns:
        Structure with file tree and statistics
        
    Example:
        >>> result = get_structure("./project")
        >>> print(result.to_string("tree"))
        >>> result.to_file("detailed.txt", detailed=True)
    """
    
    scan_path = Path(path) if isinstance(path, str) else path
    
    options = ScanOptions(
        detailed=False,
        use_gitignore=use_gitignore,
        use_default_exclusions=use_default_exclusions,
        gitignore_path=Path(gitignore_path) if gitignore_path else None,
        include_patterns=include_patterns or [],
        exclude_patterns=exclude_patterns or [],
        allow=allow or []
    )
    
    scanner = create_scanner()
    result = scanner.scan(scan_path, options)
    
    result._scan_options = options
    result._has_details = False
    
    return result


__all__ = [
    'get_structure',
    'DEFAULT_EXCLUSIONS'
]
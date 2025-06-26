"""Data models for folder structure analyzer."""

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Union
from functools import lru_cache

from .._constants import TEXT_EXTENSIONS
from .._utils import format_error_message

if TYPE_CHECKING:
    from ..scanner.api import ScanOptions


@dataclass
class FileNode:
    """File or directory node in the tree structure."""
    
    name: str
    path: Path
    is_dir: bool
    size: int = 0
    lines: Optional[int] = None
    error: Optional[str] = None
    children: List['FileNode'] = field(default_factory=list)
    
    @property
    def has_error(self) -> bool:
        return self.error is not None
    
    @property
    def total_dirs(self) -> int:
        if not self.is_dir:
            return 0
        
        count = 0
        for child in self.children:
            if child.is_dir:
                count += 1 + child.total_dirs
        return count
    
    @property
    def total_files(self) -> int:
        if not self.is_dir:
            return 1 if not self.has_error else 0
        
        return sum(child.total_files for child in self.children)
    
    @property
    def total_size(self) -> int:
        if not self.is_dir:
            return self.size if not self.has_error else 0
        
        return sum(child.total_size for child in self.children)
    
    @property
    def total_lines(self) -> int:
        if not self.is_dir:
            return self.lines or 0
        
        return sum(child.total_lines for child in self.children)
    
    def get_errors(self) -> List[tuple[Path, str]]:
        """Collect all errors from this node and children."""
        errors = []
        
        if self.has_error:
            errors.append((self.path, self.error))
        
        if self.is_dir:
            for child in self.children:
                errors.extend(child.get_errors())
        
        return errors


@dataclass
class Structure:
    """Container for scan results with formatting capabilities."""
    
    root: FileNode
    scan_time: float = 0.0
    _scan_options: Optional['ScanOptions'] = None
    _has_details: bool = False
    
    def to_string(self, format_type: str = "tree", detailed: bool = False) -> str:
        """Convert scan result to formatted string."""
        if detailed:
            self._ensure_details()
            
        # Import formatters to ensure they are registered
        from ..formatters import (
            _tree, _json, _markdown, _html, _csv, _xml, _list
        )
        
        # Create formatter instance based on format type
        formatters = {
            'tree': _tree.TreeFormatter(),
            'json': _json.JsonFormatter(),
            'json-compact': _json.CompactJsonFormatter(),
            'markdown': _markdown.MarkdownFormatter(),
            'html': _html.HtmlFormatter(),
            'csv': _csv.CsvFormatter(),
            'xml': _xml.XmlFormatter(),
            'list': _list.ListFormatter()
        }
        
        formatter = formatters.get(format_type.lower())
        if not formatter:
            raise ValueError(f"Unknown format type: {format_type}")
        
        if detailed:
            return formatter.format_detailed(self)
        else:
            return formatter.format_brief(self)
    
    def to_file(self,
                path: str | Path,
                format_type: str = "tree",
                detailed: bool = False,
                encoding: str = "utf-8") -> Path:
        """Save scan result to file."""
        file_path = Path(path) if isinstance(path, str) else path
        
        if not file_path.suffix:
            extension = self._get_extension_for_format(format_type)
            file_path = file_path.with_suffix(extension)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = self.to_string(format_type, detailed=detailed)
        
        try:
            file_path.write_text(content, encoding=encoding)
        except OSError as e:
            raise OSError(f"Failed to write file {file_path}: {e}")
        
        return file_path.resolve()
    
    def to_zip(self, path: Union[str, Path]) -> Path:
        """Create ZIP archive from scanned structure."""
        from ..archiver._zip import create_zip_from_structure
        
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        root_node = self.root
        if root_node.name == ".":
            root_node = dataclasses.replace(root_node, name=Path.cwd().name)
        
        return create_zip_from_structure(root_node, output_path)
    
    def _ensure_details(self) -> None:
        """Ensure detailed information is available."""
        if self._has_details:
            return
        
        if not self._scan_options:
            raise RuntimeError("Cannot get detailed information: scan options not saved")
        
        from ..scanner._impl import FileSystemScanner
        from ..scanner.api import ScanOptions
        
        scanner = FileSystemScanner()
        detailed_options = dataclasses.replace(self._scan_options, detailed=True)
        detailed_result = scanner.scan(self.root.path, detailed_options)
        
        self.root = detailed_result.root
        self.scan_time = detailed_result.scan_time
        self._has_details = True
    
    def _get_extension_for_format(self, format_type: str) -> str:
        """Get file extension for format type."""
        extension_map = {
            "tree": ".txt",
            "json": ".json",
            "json-compact": ".json",
            "markdown": ".md",
            "html": ".html",
            "csv": ".csv",
            "xml": ".xml",
            "list": ".txt"
        }
        
        return extension_map.get(format_type.lower(), ".txt")
    
    def get_errors(self) -> List[tuple[Path, str]]:
        """Get all errors from scan."""
        return self.root.get_errors()
    
    @property
    def statistics(self) -> dict:
        """Get scan statistics."""
        return {
            "total_dirs": 1 + self.root.total_dirs if self.root.is_dir else 0,
            "total_files": self.root.total_files,
            "total_size": self.root.total_size,
            "total_lines": self.root.total_lines,
            "scan_time": self.scan_time,
            "errors_count": len(self.get_errors())
        }


# Internal utility functions

@lru_cache(maxsize=128)
def format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 0:
        return "0 B"
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_number(num: int) -> str:
    """Format number with space as thousands separator."""
    if num < 0:
        return "0"
    
    s = str(num)
    result = []
    for i, digit in enumerate(reversed(s)):
        if i > 0 and i % 3 == 0:
            result.append(' ')
        result.append(digit)
    return ''.join(reversed(result))


def format_line_count(lines: Optional[int]) -> str:
    """Format line count for display."""
    if lines is None:
        return ""
    elif lines == 1:
        return "1 line"
    else:
        return f"{format_number(lines)} lines"


def is_text_file(path: Path) -> bool:
    """Check if file is a text file by extension."""
    return path.suffix.lower() in TEXT_EXTENSIONS


__all__ = [
    'FileNode',
    'Structure',
    'format_size',
    'format_number', 
    'format_line_count',
    'is_text_file'
]
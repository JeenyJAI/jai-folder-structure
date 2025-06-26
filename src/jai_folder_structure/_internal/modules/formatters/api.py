"""Output formatters API and base classes."""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from ..models.api import FileNode, Structure, format_size, format_number
from .._constants import INDENT_SIZE
from .._utils import format_error_message


@runtime_checkable
class FormatterProtocol(Protocol):
    """Protocol for output formatters."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get formatter name."""
        ...
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get formatter description."""
        ...
    
    @abstractmethod
    def format_brief(self, result: Structure) -> str:
        """Format scan result in brief mode."""
        ...
    
    @abstractmethod
    def format_detailed(self, result: Structure) -> str:
        """Format scan result in detailed mode."""
        ...


class BaseFormatter:
    """Base class for formatters with common functionality."""
    
    def _calculate_max_path_width(self, node: FileNode, depth: int) -> int:
        """Calculate maximum visual path width in the tree.
        
        Args:
            node: File node to calculate from
            depth: Current depth in tree
            
        Returns:
            Maximum width needed for paths
        """
        name = f"{node.name}/" if node.is_dir else node.name
        visual_width = depth * INDENT_SIZE + len(name)
        
        max_width = visual_width
        
        if node.is_dir and not node.has_error and node.children:
            for child in node.children:
                child_max = self._calculate_max_path_width(child, depth + 1)
                max_width = max(max_width, child_max)
        
        return max_width
    
    def _format_node_stats(self, node: FileNode, include_self_name: bool = False) -> str:
        """Format node statistics for display.
        
        Args:
            node: Node to format stats for
            include_self_name: Include node name in stats
            
        Returns:
            Formatted statistics string with # prefix
        """
        parts = []
        
        if include_self_name:
            # For root node in detailed view
            if node.is_dir:
                if node.total_dirs > 0 or node.total_files > 0:
                    dir_text = f"{node.total_dirs} dir{'s' if node.total_dirs != 1 else ''}"
                    file_text = f"{node.total_files} file{'s' if node.total_files != 1 else ''}"
                    parts.append(f"{dir_text}, {file_text}")
                
                if node.total_size > 0:
                    parts.append(format_size(node.total_size))
                
                if node.total_lines > 0:
                    parts.append(f"{format_number(node.total_lines)} lines")
        else:
            # For non-root nodes
            if node.is_dir:
                # Order changed to match old format:
                # 1. Number of directories and files
                # 2. Size
                # 3. Number of lines
                if node.total_dirs > 0 or node.total_files > 0:
                    dir_text = f"{node.total_dirs} dir{'s' if node.total_dirs != 1 else ''}"
                    file_text = f"{node.total_files} file{'s' if node.total_files != 1 else ''}"
                    parts.append(f"{dir_text}, {file_text}")
                
                if node.total_size > 0:
                    parts.append(format_size(node.total_size))
                
                if node.total_lines > 0:
                    parts.append(f"{format_number(node.total_lines)} lines")
            else:
                if node.size > 0:
                    parts.append(format_size(node.size))
                
                if node.lines is not None:
                    parts.append(f"{format_number(node.lines)} lines")
        
        # IMPORTANT: Add # before statistics
        return f"# {', '.join(parts)}" if parts else ""
    
    def _format_error(self, error: str) -> str:
        """Format error message for display.
        
        This method is deprecated. Use format_error_message from _utils instead.
        """
        return format_error_message(error)


def get_formats() -> list[str]:
    """Get list of available formatter names."""
    # Import formatters here to ensure they are registered
    from . import _tree, _json, _markdown, _html, _csv, _xml, _list
    
    formatters = [
        _tree.TreeFormatter(),
        _json.JsonFormatter(),
        _json.CompactJsonFormatter(),
        _markdown.MarkdownFormatter(),
        _html.HtmlFormatter(),
        _csv.CsvFormatter(),
        _xml.XmlFormatter(),
        _list.ListFormatter()
    ]
    
    return [f.name for f in formatters]


# Note: create_formatter function removed as it's no longer used
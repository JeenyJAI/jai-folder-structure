"""List formatter implementation."""

from typing import List
from datetime import datetime

from ..models.api import FileNode, Structure, format_size, format_number
from .._constants import MAX_PATH_WIDTH, DATE_FORMAT
from .._utils import build_path, calculate_padding, format_error_message
from .api import BaseFormatter, FormatterProtocol


class ListFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for flat list output."""
    
    @property
    def name(self) -> str:
        return "list"
    
    @property
    def description(self) -> str:
        return "Flat list of paths with optional statistics"
    
    def format_brief(self, result: Structure) -> str:
        lines = []
        self._collect_paths_brief(result.root, lines, "")
        return '\n'.join(lines)
    
    def format_detailed(self, result: Structure) -> str:
        lines = []
        
        # Header with # prefix
        lines.extend([
            f"# Project: {result.root.name}",
            f"# Generated: {datetime.now().strftime(DATE_FORMAT)}"
        ])
        
        errors = result.get_errors()
        scan_info = f"Scan time: {result.scan_time:.2f}s"
        if errors:
            scan_info += f" ({len(errors)} error{'s' if len(errors) != 1 else ''})"
        lines.extend([f"# {scan_info}", ""])  # Empty line after header
        
        # Calculate max width for alignment
        max_width = self._calculate_max_path_width_list(result.root, "")
        max_width = min(max_width + 3, MAX_PATH_WIDTH)
        
        self._collect_paths_detailed(result.root, lines, "", max_width)
        return '\n'.join(lines)
    
    def _calculate_max_path_width_list(self, node: FileNode, parent_path: str) -> int:
        """Calculate maximum path width in the list."""
        current_path = build_path(parent_path, node.name, node.is_dir)
        max_width = len(current_path)
        
        if node.is_dir and not node.has_error and node.children:
            for child in node.children:
                child_max = self._calculate_max_path_width_list(child, current_path.rstrip('/'))
                max_width = max(max_width, child_max)
        
        return max_width
    
    def _collect_paths_brief(self, node: FileNode, lines: List[str], parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        lines.append(current_path)
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_paths_brief(child, lines, current_path.rstrip('/'))
    
    def _collect_paths_detailed(self, node: FileNode, lines: List[str], parent_path: str, 
                                max_width: int) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        line = current_path
        
        if node.has_error:
            padding = calculate_padding(len(current_path), max_width)
            line += f"{padding}# {format_error_message(node.error or '')}"
        else:
            stats = self._format_node_stats(node)
            if stats:
                padding = calculate_padding(len(current_path), max_width)
                line += padding + stats
        
        lines.append(line)
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_paths_detailed(child, lines, current_path.rstrip('/'), max_width)
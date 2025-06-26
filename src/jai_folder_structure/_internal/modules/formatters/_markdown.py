"""Markdown formatter implementation."""

from typing import List
from datetime import datetime

from ..models.api import FileNode, Structure, format_size
from .._constants import DATE_FORMAT
from .._utils import build_path, format_error_message
from .api import BaseFormatter, FormatterProtocol


class MarkdownFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for Markdown output."""
    
    @property
    def name(self) -> str:
        return "markdown"
    
    @property
    def description(self) -> str:
        return "Markdown representation with tables and tree view"
    
    def format_brief(self, result: Structure) -> str:
        lines = [
            "| Path | Type | Error |",
            "|------|------|-------|"
        ]
        self._collect_nodes_brief(result.root, lines, "")
        return '\n'.join(lines)
    
    def format_detailed(self, result: Structure) -> str:
        lines = []
        
        # Header
        lines.extend([
            "# Project Structure",
            "",
            f"**Project:** {result.root.name}  ",
            f"**Generated:** {datetime.now().strftime(DATE_FORMAT)}  ",
        ])
        
        errors = result.get_errors()
        scan_info = f"**Scan time:** {result.scan_time:.2f}s"
        if errors:
            scan_info += f" ({len(errors)} error{'s' if len(errors) != 1 else ''})"
        lines.extend([scan_info, "", "## Files", ""])
        
        # Table
        lines.extend([
            "| Path | Type | Size | Lines | Contents | Error |",
            "|------|------|------|-------|----------|-------|"
        ])
        
        self._collect_nodes_detailed(result.root, lines, "")
        return '\n'.join(lines)
    
    def _collect_nodes_brief(self, node: FileNode, lines: List[str], parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        node_type = "dir" if node.is_dir else "file"
        error = format_error_message(node.error or '') if node.has_error else ""
        
        lines.append(f"| {current_path} | {node_type} | {error} |")
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_nodes_brief(child, lines, current_path.rstrip('/'))
    
    def _collect_nodes_detailed(self, node: FileNode, lines: List[str], parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        node_type = "dir" if node.is_dir else "file"
        
        if node.has_error:
            size = lines_str = contents = "-"
            error = format_error_message(node.error or '')
        else:
            if node.is_dir:
                size = format_size(node.total_size) if node.total_size > 0 else "-"
                lines_str = str(node.total_lines) if node.total_lines > 0 else "-"
                
                contents_parts = []
                if node.total_dirs > 0:
                    contents_parts.append(f"{node.total_dirs} dir{'s' if node.total_dirs != 1 else ''}")
                if node.total_files > 0:
                    contents_parts.append(f"{node.total_files} file{'s' if node.total_files != 1 else ''}")
                contents = ", ".join(contents_parts) if contents_parts else "-"
            else:
                size = format_size(node.size) if node.size > 0 else "-"
                lines_str = str(node.lines) if node.lines is not None else "-"
                contents = "-"
            
            error = ""
        
        lines.append(f"| {current_path} | {node_type} | {size} | {lines_str} | {contents} | {error} |")
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_nodes_detailed(child, lines, current_path.rstrip('/'))
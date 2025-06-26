"""CSV formatter implementation."""

import csv
import io
from typing import Any

from ..models.api import FileNode, Structure
from .._utils import build_path, format_error_message
from .api import BaseFormatter, FormatterProtocol


class CsvFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for CSV output."""
    
    @property
    def name(self) -> str:
        return "csv"
    
    @property
    def description(self) -> str:
        return "CSV table representation"
    
    def format_brief(self, result: Structure) -> str:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        
        writer.writerow(['path', 'is_dir', 'error'])
        self._collect_rows_brief(result.root, writer, "")
        
        return output.getvalue().rstrip()
    
    def format_detailed(self, result: Structure) -> str:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        
        writer.writerow(['path', 'is_dir', 'dirs', 'files', 'size', 'lines', 'error'])
        self._collect_rows_detailed(result.root, writer, "")
        
        return output.getvalue().rstrip()
    
    def _collect_rows_brief(self, node: FileNode, writer: Any, parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        is_dir = 'true' if node.is_dir else 'false'
        error = format_error_message(node.error or '') if node.has_error else ''
        
        writer.writerow([current_path, is_dir, error])
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_rows_brief(child, writer, current_path.rstrip('/'))
    
    def _collect_rows_detailed(self, node: FileNode, writer: Any, parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        is_dir = 'true' if node.is_dir else 'false'
        
        if node.is_dir:
            dirs = str(node.total_dirs) if not node.has_error else '0'
            files = str(node.total_files) if not node.has_error else '0'
            size = str(node.total_size) if not node.has_error else '0'
            lines = str(node.total_lines) if not node.has_error else '0'
        else:
            dirs = ''
            files = ''
            size = str(node.size) if not node.has_error else '0'
            lines = str(node.lines) if node.lines is not None and not node.has_error else ''
        
        error = format_error_message(node.error or '') if node.has_error else ''
        
        writer.writerow([current_path, is_dir, dirs, files, size, lines, error])
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._collect_rows_detailed(child, writer, current_path.rstrip('/'))
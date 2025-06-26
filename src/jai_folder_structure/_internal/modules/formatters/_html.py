"""HTML formatter implementation."""

import html
from typing import List
from datetime import datetime

from ..models.api import FileNode, Structure, format_size, format_number
from .._constants import MAX_PATH_WIDTH, DATE_FORMAT, INDENT_SIZE
from .._utils import calculate_padding, format_error_message
from .api import BaseFormatter, FormatterProtocol


class HtmlFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for HTML output."""
    
    @property
    def name(self) -> str:
        return "html"
    
    @property
    def description(self) -> str:
        return "HTML page with styled tree view"
    
    def format_brief(self, result: Structure) -> str:
        lines = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '    <title>Folder Structure</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 20px; }',
            '        pre { font-family: monospace; font-size: 14px; }',
            '        .error { color: #d32f2f; }',
            '    </style>',
            '</head>',
            '<body>',
            '    <h1>Folder Structure</h1>',
            '    <pre>'
        ]
        
        self._format_tree_html_brief(result.root, lines, "", is_root=True)
        
        lines.extend([
            '    </pre>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(lines)
    
    def format_detailed(self, result: Structure) -> str:
        lines = []
        
        # HTML header with styles
        lines.extend(self._build_html_header(result))
        
        # Calculate max width for alignment
        max_width = self._calculate_max_path_width(result.root, 0)
        max_width = min(max_width + 3, MAX_PATH_WIDTH)
        
        # Tree content
        lines.extend([
            '        <div class="tree">',
            '            <h2>Structure</h2>',
            '            <pre>'
        ])
        
        self._format_tree_html_detailed(result.root, lines, "", max_width, depth=0, is_root=True)
        
        # HTML footer
        lines.extend([
            '            </pre>',
            '        </div>',
            '    </div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(lines)
    
    def _build_html_header(self, result: Structure) -> List[str]:
        """Build HTML header with metadata."""
        errors = result.get_errors()
        scan_info = f"{result.scan_time:.2f}s"
        if errors:
            scan_info += f" ({len(errors)} error{'s' if len(errors) != 1 else ''})"
        
        return [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'    <title>Folder Structure: {html.escape(str(result.root.name))}</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }',
            '        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }',
            '        .header { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }',
            '        .header h1 { margin: 0 0 10px 0; color: #333; }',
            '        .header p { margin: 5px 0; color: #666; }',
            '        .tree { background: #f8f8f8; padding: 15px; font-family: monospace; font-size: 14px; border-radius: 5px; overflow-x: auto; }',
            '        .tree h2 { font-family: Arial, sans-serif; color: #333; font-size: 1.3em; margin-top: 0; }',
            '        .tree pre { margin: 0; }',
            '        .error { color: #d32f2f; }',
            '        .stats { color: #666; }',
            '    </style>',
            '</head>',
            '<body>',
            '    <div class="container">',
            '        <div class="header">',
            '            <h1>Project Structure</h1>',
            f'            <p><strong>Path:</strong> {html.escape(str(result.root.name))}</p>',
            f'            <p><strong>Generated:</strong> {datetime.now().strftime(DATE_FORMAT)}</p>',
            f'            <p><strong>Scan time:</strong> {scan_info}</p>',
            '        </div>'
        ]
    
    def _format_tree_html_brief(self, node: FileNode, lines: List[str], prefix: str,
                               is_root: bool = False, is_last: bool = True) -> None:
        if is_root:
            line = html.escape(f"{node.name}/")
            if node.has_error:
                line += f'  <span class="error"># {html.escape(format_error_message(node.error or ""))}</span>'
            lines.append(line)
            
            for i, child in enumerate(node.children):
                is_last_child = i == len(node.children) - 1
                self._format_tree_html_brief(child, lines, "", False, is_last_child)
        else:
            connector = "└─ " if is_last else "├─ "
            name = f"{node.name}/" if node.is_dir else node.name
            line = html.escape(f"{prefix}{connector}{name}")
            
            if node.has_error:
                line += f'  <span class="error"># {html.escape(format_error_message(node.error or ""))}</span>'
            
            lines.append(line)
            
            if node.is_dir and not node.has_error:
                extension = "   " if is_last else "│  "
                new_prefix = prefix + extension
                
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_tree_html_brief(child, lines, new_prefix, False, is_last_child)
    
    def _format_tree_html_detailed(self, node: FileNode, lines: List[str], prefix: str,
                                  max_width: int, depth: int, is_root: bool = False, 
                                  is_last: bool = True) -> None:
        if is_root:
            name = f"{node.name}/"
            line_start = html.escape(name)
        else:
            connector = "└─ " if is_last else "├─ "
            name = f"{node.name}/" if node.is_dir else node.name
            line_start = html.escape(f"{prefix}{connector}{name}")
        
        visual_width = depth * INDENT_SIZE + len(f"{node.name}/" if node.is_dir else node.name)
        
        if node.has_error:
            line = line_start + f'  <span class="error"># {html.escape(format_error_message(node.error or ""))}</span>'
        else:
            stats = self._format_node_stats(node, include_self_name=(depth == 0))
            if stats:
                padding = html.escape(calculate_padding(visual_width, max_width))
                line = line_start + padding + f'<span class="stats">{html.escape(stats)}</span>'
            else:
                line = line_start
        
        lines.append(line)
        
        if node.is_dir and not node.has_error:
            if is_root:
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_tree_html_detailed(child, lines, "", max_width, 
                                                  depth + 1, False, is_last_child)
            else:
                extension = "   " if is_last else "│  "
                new_prefix = prefix + extension
                
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_tree_html_detailed(child, lines, new_prefix, max_width, 
                                                  depth + 1, False, is_last_child)
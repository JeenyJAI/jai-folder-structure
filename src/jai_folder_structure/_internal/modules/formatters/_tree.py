"""Tree formatter implementation."""

from typing import List
from datetime import datetime

from ..models.api import FileNode, Structure, format_size, format_number
from .._constants import (
    MAX_PATH_WIDTH, 
    DATE_FORMAT, 
    INDENT_SIZE,
    TREE_PIPE,
    TREE_TEE,
    TREE_ELBOW,
    TREE_BRANCH
)
from .._utils import build_path, calculate_padding, format_error_message
from .api import BaseFormatter, FormatterProtocol


class TreeFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for tree-style output."""
    
    @property
    def name(self) -> str:
        return "tree"
    
    @property
    def description(self) -> str:
        return "Text tree representation with optional statistics"
    
    def format_brief(self, result: Structure) -> str:
        lines = []
        self._format_node_brief(result.root, lines, "", is_root=True)
        return '\n'.join(lines)
    
    def format_detailed(self, result: Structure) -> str:
        lines = []
        lines.extend(self._format_header(result))
        
        max_width = self._calculate_max_path_width(result.root, depth=0)
        max_width = min(max_width + 3, MAX_PATH_WIDTH)  # Add minimum spacing
        
        self._format_node_detailed(result.root, lines, "", max_width, depth=0, is_root=True)
        return '\n'.join(lines)
    
    def _format_header(self, result: Structure) -> List[str]:
        header = []
        header.append(f"# Project: {result.root.name}")
        header.append(f"# Generated: {datetime.now().strftime(DATE_FORMAT)}")
        
        errors = result.get_errors()
        scan_info = f"Scan time: {result.scan_time:.2f}s"
        if errors:
            scan_info += f" ({len(errors)} error{'s' if len(errors) != 1 else ''})"
        header.append(f"# {scan_info}")
        header.append("")  # Empty line after header
        
        return header
    
    def _format_node_brief(self, node: FileNode, lines: List[str], prefix: str, 
                          is_root: bool = False, is_last: bool = True) -> None:
        if is_root:
            line = f"{node.name}/"
            if node.has_error:
                line += f"  # {format_error_message(node.error or '')}"
            lines.append(line)
            
            for i, child in enumerate(node.children):
                is_last_child = i == len(node.children) - 1
                self._format_node_brief(child, lines, "", False, is_last_child)
        else:
            connector = f"{TREE_ELBOW}{TREE_BRANCH} " if is_last else f"{TREE_TEE}{TREE_BRANCH} "
            name = f"{node.name}/" if node.is_dir else node.name
            line = f"{prefix}{connector}{name}"
            
            if node.has_error:
                line += f"  # {format_error_message(node.error or '')}"
            
            lines.append(line)
            
            if node.is_dir and not node.has_error:
                extension = "   " if is_last else f"{TREE_PIPE}  "
                new_prefix = prefix + extension
                
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_node_brief(child, lines, new_prefix, False, is_last_child)
    
    def _format_node_detailed(self, node: FileNode, lines: List[str], prefix: str, 
                             max_width: int, depth: int, is_root: bool = False, 
                             is_last: bool = True) -> None:
        if is_root:
            name = f"{node.name}/"
            line_start = name
        else:
            connector = f"{TREE_ELBOW}{TREE_BRANCH} " if is_last else f"{TREE_TEE}{TREE_BRANCH} "
            name = f"{node.name}/" if node.is_dir else node.name
            line_start = f"{prefix}{connector}{name}"
        
        visual_width = depth * INDENT_SIZE + len(name)
        
        if node.has_error:
            line = f"{line_start}  # {format_error_message(node.error or '')}"
        else:
            stats = self._format_node_stats(node, include_self_name=(depth == 0))
            if stats:
                padding = calculate_padding(visual_width, max_width)
                line = f"{line_start}{padding}{stats}"
            else:
                line = line_start
        
        lines.append(line)
        
        if node.is_dir and not node.has_error:
            if is_root:
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_node_detailed(child, lines, "", max_width, 
                                             depth + 1, False, is_last_child)
            else:
                extension = "   " if is_last else f"{TREE_PIPE}  "
                new_prefix = prefix + extension
                
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    self._format_node_detailed(child, lines, new_prefix, max_width, 
                                             depth + 1, False, is_last_child)
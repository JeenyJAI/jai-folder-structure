"""JSON formatter implementation."""

import json
from datetime import datetime
from typing import Dict, Any

from ..models.api import FileNode, Structure
from .._constants import ISO_DATE_FORMAT
from .._utils import build_path, format_error_message
from .api import BaseFormatter, FormatterProtocol


class JsonFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for JSON output."""
    
    @property
    def name(self) -> str:
        return "json"
    
    @property
    def description(self) -> str:
        return "JSON representation with optional metadata"
    
    def format_brief(self, result: Structure) -> str:
        data = {"root": self._node_to_dict_brief(result.root, "")}
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def format_detailed(self, result: Structure) -> str:
        data = {
            "root": self._node_to_dict_detailed(result.root, ""),
            "metadata": {
                "created": datetime.now().strftime(ISO_DATE_FORMAT),
                "scan_time": result.scan_time,
                "errors_count": len(result.get_errors()),
                "version": "1.0"
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _node_to_dict_brief(self, node: FileNode, parent_path: str) -> Dict[str, Any]:
        current_path = build_path(parent_path, node.name, node.is_dir)
        
        data: Dict[str, Any] = {
            "name": node.name,
            "path": current_path,
            "is_dir": node.is_dir,
            "error": format_error_message(node.error or '') if node.has_error else None
        }
        
        if node.is_dir:
            data["children"] = [
                self._node_to_dict_brief(child, current_path.rstrip('/')) 
                for child in node.children
            ] if node.children and not node.has_error else []
        
        return data
    
    def _node_to_dict_detailed(self, node: FileNode, parent_path: str) -> Dict[str, Any]:
        current_path = build_path(parent_path, node.name, node.is_dir)
        
        data: Dict[str, Any] = {
            "name": node.name,
            "path": current_path,
            "is_dir": node.is_dir
        }
        
        if node.is_dir:
            data.update({
                "size": node.total_size,
                "dirs": node.total_dirs,
                "files": node.total_files,
                "lines": node.total_lines
            })
        else:
            data["size"] = node.size
            if node.lines is not None:
                data["lines"] = node.lines
        
        data["error"] = format_error_message(node.error or '') if node.has_error else None
        
        if node.is_dir:
            data["children"] = [
                self._node_to_dict_detailed(child, current_path.rstrip('/')) 
                for child in node.children
            ] if node.children and not node.has_error else []
        
        return data


class CompactJsonFormatter(JsonFormatter):
    """Formatter for compact JSON output (no indentation)."""
    
    @property
    def name(self) -> str:
        return "json-compact"
    
    @property
    def description(self) -> str:
        return "Compact JSON representation (single line)"
    
    def format_brief(self, result: Structure) -> str:
        data = {"root": self._node_to_dict_brief(result.root, "")}
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    
    def format_detailed(self, result: Structure) -> str:
        data = {
            "root": self._node_to_dict_detailed(result.root, ""),
            "metadata": {
                "created": datetime.now().strftime(ISO_DATE_FORMAT),
                "scan_time": result.scan_time,
                "errors_count": len(result.get_errors()),
                "version": "1.0"
            }
        }
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
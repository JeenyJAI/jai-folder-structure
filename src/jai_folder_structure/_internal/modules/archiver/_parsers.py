"""Parsers for different text structure formats."""

import re
import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple, Optional
from io import StringIO

from .._utils import batch_replace, normalize_path_separators, is_path_traversal_attempt


ASCII_INDENT_CHARS = {' ', '│', '├', '└', '─', '-', '–', '—'}
TAB_CHAR = '\t'
COMMENT_PATTERN = re.compile(r'^(.*?)(?:#|//)')


def parse_structure_file(content: str, format_type: str) -> Dict[str, Any]:
    """Parse structure from text file content."""
    format_lower = format_type.lower()
    
    if format_lower == "tree":
        return _parse_tree_format(content)
    elif format_lower == "list":
        return _parse_list_format(content)
    elif format_lower == "json":
        return _parse_json_format(content)
    elif format_lower == "csv":
        return _parse_csv_format(content)
    elif format_lower == "xml":
        return _parse_xml_format(content)
    else:
        raise ValueError(f"Unknown format: '{format_type}'. Available formats: tree, list, json, csv, xml")


def _parse_json_format(content: str) -> Dict[str, Any]:
    """Parse JSON format structure."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    
    # Handle both simple {"name": {...}} and full format with root/metadata
    if "root" in data and isinstance(data["root"], dict):
        # Full format from formatters
        return _convert_json_node_to_dict(data["root"])
    else:
        # Simple format - direct structure
        return _convert_json_structure_to_dict(data)


def _convert_json_node_to_dict(node: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON node format to internal dict structure."""
    name = node.get("name", "")
    is_dir = node.get("is_dir", True)
    
    # Handle root node (when called with the root of the JSON)
    if is_dir:
        result = {}
        
        # Process children if present
        if "children" in node and isinstance(node["children"], list):
            for child in node["children"]:
                child_name = child.get("name", "")
                if not child_name:
                    continue
                
                if child.get("is_dir", True):
                    # Recursively process directory
                    child_dict = _convert_json_node_to_dict(child)
                    # Extract content if wrapped
                    if child_name in child_dict and len(child_dict) == 1:
                        result[child_name] = child_dict[child_name]
                    else:
                        result[child_name] = child_dict
                else:
                    # File
                    result[child_name] = ""
        
        # Wrap in name if present
        if name:
            if result:  # Has children
                return {name: result}
            else:  # Empty directory
                return {name: {}}
        else:
            return result
    else:
        # This shouldn't happen at top level, return empty dict
        return {}


def _convert_json_structure_to_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert simple JSON structure to internal dict format."""
    result = {}
    
    for name, value in data.items():
        if isinstance(value, dict):
            # Directory
            result[name] = _convert_json_structure_to_dict(value)
        elif value is None or value == "":
            # File
            result[name] = ""
        else:
            # Skip invalid entries
            continue
    
    return result


def _parse_csv_format(content: str) -> Dict[str, Any]:
    """Parse CSV format structure."""
    reader = csv.DictReader(StringIO(content))
    
    if not reader.fieldnames:
        raise ValueError("CSV file has no headers")
    
    # Check required columns
    required_columns = {"path"}
    if not required_columns.issubset(set(reader.fieldnames)):
        raise ValueError("CSV must have 'path' column")
    
    result = {}
    paths_processed = 0
    
    for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is 1)
        path = row.get("path", "").strip()
        if not path:
            continue
        
        # Check for path traversal
        if is_path_traversal_attempt(path):
            raise ValueError(f"Path traversal not allowed: '{path}' at row {row_num}")
        
        # Normalize path
        normalized_path = normalize_path_separators(path)
        
        # Determine if directory (by is_dir column or trailing slash)
        is_dir = False
        if "is_dir" in row:
            is_dir_value = row["is_dir"].strip().lower()
            is_dir = is_dir_value in ("true", "1", "yes", "y")
        elif path.endswith("/"):
            is_dir = True
            normalized_path = normalized_path.rstrip("/")
        
        # Build structure
        parts = [p for p in normalized_path.split("/") if p]
        
        if not parts:
            continue
        
        current = result
        for i, part in enumerate(parts):
            if part == '.' or part == '..':
                raise ValueError(f"Invalid path segment '{part}' at row {row_num}")
            
            if i == len(parts) - 1 and not is_dir:
                # Last part is a file
                if part in current:
                    raise ValueError(f"Duplicate path '{normalized_path}' at row {row_num}")
                current[part] = ""
            else:
                # Directory
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValueError(f"Path conflict at '{normalized_path}' row {row_num}")
                current = current[part]
        
        paths_processed += 1
    
    if paths_processed == 0:
        raise ValueError("No valid paths found in CSV")
    
    return result


def _parse_xml_format(content: str) -> Dict[str, Any]:
    """Parse XML format structure."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")
    
    # Handle both <jai_folder_structure> wrapper and direct <node>
    if root.tag == "jai_folder_structure":
        # Find first node child
        node = root.find("node")
        if node is None:
            raise ValueError("No <node> element found in XML")
    elif root.tag == "node":
        node = root
    else:
        raise ValueError(f"Unexpected root element: <{root.tag}>")
    
    return _convert_xml_node_to_dict(node)


def _convert_xml_node_to_dict(node: ET.Element) -> Dict[str, Any]:
    """Convert XML node to internal dict structure."""
    name = node.get("name", "")
    is_dir = node.get("is_dir", "true").lower() == "true"
    
    # For root level processing or nodes without name
    if not name and node.tag == "node":
        # Root node without name - process children directly
        result = {}
        for child in node:
            if child.tag == "node":
                child_name = child.get("name", "")
                if child_name:
                    child_is_dir = child.get("is_dir", "true").lower() == "true"
                    if child_is_dir:
                        # Get the content without wrapping
                        child_content = _process_xml_children(child)
                        result[child_name] = child_content
                    else:
                        result[child_name] = ""
        return result
    
    if is_dir:
        children = _process_xml_children(node)
        
        if name:
            return {name: children}
        else:
            return children
    else:
        # File node at top level - shouldn't happen, return empty dict
        return {}


def _process_xml_children(node: ET.Element) -> Dict[str, Any]:
    """Process children of XML node without wrapping in parent name."""
    children = {}
    for child in node:
        if child.tag == "node":
            child_name = child.get("name", "")
            if not child_name:
                continue
            
            child_is_dir = child.get("is_dir", "true").lower() == "true"
            if child_is_dir:
                # Recursively process directory children
                children[child_name] = _process_xml_children(child)
            else:
                # File
                children[child_name] = ""
    return children


# Keep existing functions as is
def _strip_comment(line: str) -> str:
    """Remove comment from line."""
    match = COMMENT_PATTERN.match(line)
    if match:
        return match.group(1).rstrip()
    return line.rstrip()


def _parse_list_format(content: str) -> Dict[str, Any]:
    """Parse simple path list (one path per line)."""
    lines = content.strip().split('\n')
    if not lines or not any(line.strip() for line in lines):
        raise ValueError("Empty input file")
    
    result = {}
    valid_paths = 0
    
    for line_num, line in enumerate(lines, 1):
        line = _strip_comment(line).strip()
        if not line:
            continue
        
        if is_path_traversal_attempt(line):
            raise ValueError(f"Path traversal not allowed: '{line}' at line {line_num}")
        
        normalized_path = normalize_path_separators(line)
        path_parts = normalized_path.split('/')
        
        for part in path_parts:
            if part == '.' or part == '..':
                raise ValueError(f"Invalid path segment '{part}' at line {line_num}")
        
        if TAB_CHAR in line:
            raise ValueError(f"Invalid character: TAB found in path at line {line_num}")
        
        is_dir = line.endswith('/')
        parts = [p for p in path_parts if p]
        
        for part in parts:
            if not part or part != part.strip():
                raise ValueError(f"Invalid path segment at line {line_num}")
            if TAB_CHAR in part:
                raise ValueError(f"Invalid character: TAB found in name '{part}' at line {line_num}")
        
        current = result
        
        if is_dir:
            for part in parts:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValueError(f"Duplicate name '{part}' at line {line_num}")
                current = current[part]
        else:
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    if part in current:
                        raise ValueError(f"Duplicate name '{part}' at line {line_num}")
                    current[part] = ""
                else:
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        raise ValueError(f"Duplicate name '{part}' at line {line_num}")
                    current = current[part]
        
        valid_paths += 1
    
    if valid_paths == 0:
        raise ValueError("No valid paths found in input")
    
    return result


def _parse_tree_format(content: str) -> Dict[str, Any]:
    """Parse content in tree format with visual hierarchy."""
    lines = content.strip().split('\n')
    if not lines or not any(line.strip() for line in lines):
        raise ValueError("Empty input file")
    
    result = {}
    open_stack: List[Tuple[int, Dict[str, Any]]] = []
    valid_entries = 0
    indent_mode: Optional[str] = None
    
    for line_num, line in enumerate(lines, 1):
        line = _strip_comment(line)
        
        if not line.strip():
            continue
        
        level, name, indent_mode = _parse_tree_line(line, line_num, indent_mode)
        
        if not name:
            continue
        
        if level == 0 and name == "./":
            open_stack = [(0, result)]
            valid_entries += 1
            continue
        
        is_dir = name.endswith('/')
        if is_dir:
            name = name[:-1]
        
        if not name:
            raise ValueError(f"Empty directory name at line {line_num}")
        
        if TAB_CHAR in name:
            raise ValueError(f"Invalid character: TAB found in name '{name}' at line {line_num}")
        
        while open_stack and open_stack[-1][0] >= level:
            open_stack.pop()
        
        parent = open_stack[-1][1] if open_stack else result
        
        if name in parent:
            raise ValueError(f"Duplicate name '{name}' at line {line_num}")
        
        if is_dir:
            parent[name] = {}
            open_stack.append((level, parent[name]))
        else:
            parent[name] = ""
        
        valid_entries += 1
    
    if valid_entries == 0:
        raise ValueError("No valid structure entries found")
    
    return result


def _parse_tree_line(line: str, line_num: int, indent_mode: Optional[str]) -> Tuple[int, str, Optional[str]]:
    """Parse tree format line and return (level, name, indent_mode)."""
    indent_end = 0
    for i, char in enumerate(line):
        if char in ASCII_INDENT_CHARS or char == TAB_CHAR:
            indent_end = i + 1
        else:
            break
    
    indent_prefix = line[:indent_end]
    remainder = line[indent_end:].rstrip()
    
    if indent_prefix and indent_mode is None:
        if TAB_CHAR in indent_prefix:
            indent_mode = 'tab'
        else:
            indent_mode = 'ascii'
    
    if indent_prefix and indent_mode is not None:
        if indent_mode == 'tab':
            for char in indent_prefix:
                if char != TAB_CHAR:
                    raise ValueError(
                        f"Mixed indentation: non-TAB character found in TAB mode at line {line_num}"
                    )
        else:
            if TAB_CHAR in indent_prefix:
                raise ValueError(
                    f"Mixed indentation: TAB character found in ASCII mode at line {line_num}"
                )
    
    level = len(indent_prefix)
    
    return level, remainder, indent_mode
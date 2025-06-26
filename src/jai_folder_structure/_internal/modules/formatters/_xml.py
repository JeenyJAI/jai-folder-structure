"""XML formatter implementation."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

from ..models.api import FileNode, Structure
from .._constants import ISO_DATE_FORMAT
from .._utils import build_path, format_error_message
from .api import BaseFormatter, FormatterProtocol


class XmlFormatter(BaseFormatter, FormatterProtocol):
    """Formatter for XML output."""
    
    @property
    def name(self) -> str:
        return "xml"
    
    @property
    def description(self) -> str:
        return "XML structured representation"
    
    def format_brief(self, result: Structure) -> str:
        root = ET.Element('jai_folder_structure')
        self._add_node_brief(result.root, root, "")
        return self._prettify_xml(root)
    
    def format_detailed(self, result: Structure) -> str:
        root = ET.Element('jai_folder_structure', {
            'version': '1.0',
            'created': datetime.now().strftime(ISO_DATE_FORMAT),
            'scan_time': f"{result.scan_time:.2f}",
            'errors_count': str(len(result.get_errors()))
        })
        self._add_node_detailed(result.root, root, "")
        return self._prettify_xml(root)
    
    def _add_node_brief(self, node: FileNode, parent: ET.Element, parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        
        attrs = {
            'name': node.name,
            'path': current_path,
            'is_dir': 'true' if node.is_dir else 'false'
        }
        
        if node.has_error:
            attrs['error'] = format_error_message(node.error or '')
        
        node_elem = ET.SubElement(parent, 'node', attrs)
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._add_node_brief(child, node_elem, current_path.rstrip('/'))
    
    def _add_node_detailed(self, node: FileNode, parent: ET.Element, parent_path: str) -> None:
        current_path = build_path(parent_path, node.name, node.is_dir)
        
        attrs = {
            'name': node.name,
            'path': current_path,
            'is_dir': 'true' if node.is_dir else 'false'
        }
        
        if node.is_dir:
            attrs.update({
                'dirs': str(node.total_dirs),
                'files': str(node.total_files),
                'size': str(node.total_size),
                'lines': str(node.total_lines)
            })
        else:
            attrs['size'] = str(node.size)
            if node.lines is not None:
                attrs['lines'] = str(node.lines)
        
        if node.has_error:
            attrs['error'] = format_error_message(node.error or '')
        
        node_elem = ET.SubElement(parent, 'node', attrs)
        
        if node.is_dir and not node.has_error:
            for child in node.children:
                self._add_node_detailed(child, node_elem, current_path.rstrip('/'))
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent='    ', encoding=None)
        
        # Remove empty lines
        lines = [line for line in pretty.split('\n') if line.strip()]
        return '\n'.join(lines)
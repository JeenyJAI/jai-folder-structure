"""Builder for converting dictionary structure to FileNode tree."""

from typing import Dict, Any
from pathlib import Path

from ..models.api import FileNode


def build_file_nodes(structure: Dict[str, Any], parent_path: Path = Path(".")) -> FileNode:
    """Build FileNode tree from dictionary structure."""
    if not structure:
        return FileNode(
            name=parent_path.name,
            path=parent_path,
            is_dir=True,
            children=[]
        )
    
    if len(structure) == 1:
        root_name = next(iter(structure))
        root_content = structure[root_name]
        
        if isinstance(root_content, dict):
            root_path = parent_path / root_name
            root_node = FileNode(
                name=root_name,
                path=root_path,
                is_dir=True,
                children=[]
            )
            
            for child_name, child_content in root_content.items():
                child_node = _build_node(child_name, child_content, root_path)
                root_node.children.append(child_node)
            
            return root_node
    
    root_node = FileNode(
        name=parent_path.name,
        path=parent_path,
        is_dir=True,
        children=[]
    )
    
    for name, content in structure.items():
        child_node = _build_node(name, content, parent_path)
        root_node.children.append(child_node)
    
    return root_node


def _build_node(name: str, content: Any, parent_path: Path) -> FileNode:
    """Build a single FileNode."""
    node_path = parent_path / name
    
    if isinstance(content, dict):
        node = FileNode(
            name=name,
            path=node_path,
            is_dir=True,
            children=[]
        )
        
        for child_name, child_content in content.items():
            child_node = _build_node(child_name, child_content, node_path)
            node.children.append(child_node)
    else:
        node = FileNode(
            name=name,
            path=node_path,
            is_dir=False,
            size=0,
            lines=None
        )
    
    return node
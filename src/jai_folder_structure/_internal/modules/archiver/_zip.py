"""ZIP archive creation from FileNode structure."""

import zipfile
import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager

from .._constants import ERRNO_NO_SPACE_LEFT
from ..models.api import FileNode


@contextmanager
def temporary_directory(prefix: str = "folder_structure_"):
    """Context manager for temporary directory with guaranteed cleanup."""
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    temp_path = Path(temp_dir)
    
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path, ignore_errors=True)


def create_zip_from_structure(root_node: FileNode, output_path: Path) -> Path:
    """Create ZIP archive from FileNode structure."""
    with temporary_directory() as temp_dir:
        create_file_structure(root_node, temp_dir)
        create_zip_from_directory(temp_dir, output_path, root_node.name)
    
    return output_path.resolve()


def create_file_structure(node: FileNode, parent_path: Path, is_root: bool = True) -> None:
    """Recursively create file structure from FileNode."""
    if is_root:
        node_path = parent_path / node.name
    else:
        node_path = parent_path
    
    if node.is_dir:
        try:
            node_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise OSError(f"Failed to create directory '{node_path}': {e}")
        
        if node.children:
            for child in node.children:
                child_path = node_path / child.name
                create_file_structure(child, child_path, is_root=False)
    else:
        try:
            node_path.parent.mkdir(parents=True, exist_ok=True)
            node_path.touch()
        except Exception as e:
            raise OSError(f"Failed to create file '{node_path}': {e}")


def create_zip_from_directory(source_dir: Path, output_path: Path, root_name: str) -> None:
    """Create ZIP archive from directory."""
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            root_dir = source_dir / root_name
            
            if not root_dir.exists():
                root_dir = source_dir
                archive_base = ""
            else:
                archive_base = root_name
            
            for item_path in root_dir.rglob('*'):
                try:
                    rel_path = item_path.relative_to(root_dir)
                except ValueError:
                    continue
                
                if archive_base:
                    archive_path = Path(archive_base) / rel_path
                else:
                    archive_path = rel_path
                
                if item_path.is_dir():
                    zipf.write(item_path, str(archive_path) + '/')
                else:
                    zipf.write(item_path, str(archive_path))
    
    except PermissionError:
        raise OSError(f"Permission denied creating archive: '{output_path}'")
    except OSError as e:
        if e.errno == ERRNO_NO_SPACE_LEFT:
            raise OSError("No space left on device")
        raise OSError(f"Failed to create archive: {e}")
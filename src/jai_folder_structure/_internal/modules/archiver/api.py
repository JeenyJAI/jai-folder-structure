"""Public API for archiver module."""

from pathlib import Path
from typing import Union

from ..models.api import FileNode
from .._utils import validate_path_length
from ._zip import create_zip_from_structure
from ._parsers import parse_structure_file
from ._validation import validate_structure
from ._builder import build_file_nodes


def make_zip(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    format: str = "tree",
    encoding: str = "utf-8"
) -> Path:
    """Create ZIP archive from text file structure description.
    
    Args:
        input_file: Path to text file with structure description
        output_file: Path for output ZIP file
        format: Format of input file ("tree", "list", "json", "csv", "xml")
        encoding: Text file encoding
        
    Returns:
        Path to created ZIP file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If format unknown, parsing fails, or validation fails
        OSError: If file system operations fail
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    supported_formats = ("tree", "list", "json", "csv", "xml")
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if format.lower() not in supported_formats:
        raise ValueError(f"Unknown format: '{format}'. Available formats: {', '.join(supported_formats)}")
    
    try:
        content = input_path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        raise ValueError(f"Failed to decode file with {encoding} encoding: {e}")
    except Exception as e:
        raise OSError(f"Failed to read input file: {e}")
    
    try:
        structure_dict = parse_structure_file(content, format)
    except Exception as e:
        raise ValueError(f"Failed to parse structure: {e}")
    
    try:
        is_valid, messages = validate_structure(structure_dict)
        if not is_valid:
            error_msg = "Validation failed:\n" + "\n".join(f"  - {msg}" for msg in messages)
            raise ValueError(error_msg)
    except Exception as e:
        if "Validation failed" in str(e):
            raise
        raise ValueError(f"Validation failed: {e}")
    
    root_node = build_file_nodes(structure_dict)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    return create_zip_from_structure(root_node, output_path)


__all__ = ['make_zip']
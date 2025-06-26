"""Folder Structure Analyzer Library.

A Python library for analyzing and visualizing directory structures with support
for multiple output formats (tree, JSON, Markdown, HTML, CSV, XML, list) and 
gitignore filtering.

Basic usage:
    >>> from jai_folder_structure import get_structure
    >>> # Fast scan by default
    >>> result = get_structure("./my_project")
    >>> print(result.to_string("tree"))
    
    >>> # Save with details (auto-rescans if needed)
    >>> result.to_file("structure.txt", detailed=True)
    
    >>> # Clean output with filters
    >>> result = get_structure("./my_project", 
    ...                       use_gitignore=True,
    ...                       use_default_exclusions=True)
    
    >>> # Create ZIP from scanned structure
    >>> result.to_zip("project_backup.zip")
    
    >>> # Create ZIP from text description
    >>> from jai_folder_structure import make_zip
    >>> make_zip("structure.txt", "output.zip", format="tree")

Main features:
    - Multiple output formats: tree, JSON, Markdown, HTML, CSV, XML, list
    - Fast scanning by default, detailed information on demand
    - Gitignore support (opt-in)
    - Default exclusions (opt-in)
    - Include/exclude patterns
    - File size and line counting
    - Error handling without crashes
    - ZIP archive creation from structures
"""

# Version information
__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Import main components from internal modules
from ._internal.modules.models.api import (
    FileNode,
    Structure
)

from ._internal.modules._constants import (
    TEXT_EXTENSIONS
)

from ._internal.modules.scanner.api import (
    get_structure,
    DEFAULT_EXCLUSIONS
)

from ._internal.modules.formatters.api import (
    get_formats
)

# Import archiver to ensure to_zip method is added to Structure
from ._internal.modules.archiver import api as _archiver_api
from ._internal.modules.archiver.api import make_zip

# Define public API - minimal and clean
__all__ = [
    "get_structure",         # Main function for analyzing
    "FileNode",              # File/directory data structure
    "Structure",             # Directory structure with to_string() and to_file() methods
    "TEXT_EXTENSIONS",       # Set of text file extensions
    "DEFAULT_EXCLUSIONS",    # Default exclusion patterns
    "get_formats",           # Get list of available formats
    "make_zip",              # Create ZIP from text structure description
    "__version__"            # Library version
]
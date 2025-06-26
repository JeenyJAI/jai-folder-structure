# jai-folder-structure

## 100% AI Code · Human Reviewed

[![PyPI](https://img.shields.io/pypi/v/jai-folder-structure)](https://pypi.org/project/jai-folder-structure/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![AI Generated](https://img.shields.io/badge/AI%20Generated-100%25-purple.svg)](https://github.com/JeenyJAI/jai-folder-structure)

Python library for analyzing and visualizing directory structures with multiple output formats, filtering, and ZIP archive creation.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Output Formats](#output-formats)
- [Usage Examples](#usage-examples)
- [Filtering](#filtering)
- [Error Handling](#error-handling)
- [Supported Extensions](#supported-extensions-for-line-counting)
- [Default Exclusions](#default-exclusions)
- [Requirements](#requirements)
- [Known Limitations](#known-limitations)
- [License](#license)

## Features

- **8 output formats**: tree, json, json-compact, markdown, html, csv, xml, list
- **Two display modes**: brief and detailed
- **Fast scanning by default**: details loaded on demand
- **ZIP archive creation**: from scanned structure or text description (5 formats)
- **.gitignore support**: automatically respects ignore rules
- **Flexible filtering**: file inclusion/exclusion patterns
- **Detailed statistics**: file sizes, lines of code count, directory statistics
- **Smart error handling**: continues on access errors
- **Lines of code counting**: automatic for 40+ text file types
- **Platforms**: Windows, Linux, macOS

## Installation

```bash
pip install jai-folder-structure
```

Or from source:

```bash
git clone https://github.com/JeenyJAI/jai-folder-structure.git
cd jai_folder_structure
pip install .
```

## Quick Start

```python
from jai_folder_structure import get_structure, make_zip

# Fast scan (default)
result = get_structure("./my_project")
print(result.to_string("tree"))

# Output with details (auto-rescans if needed)
print(result.to_string("tree", detailed=True))

# Save to file
result.to_file("structure.txt", format_type="tree", detailed=True)

# Create ZIP archive from scanned structure
zip_path = result.to_zip("project_backup.zip")

# Create ZIP from text description
make_zip("structure.txt", "project.zip", format="tree")
```

## API Reference

### Main Function

```python
get_structure(
    path: str | Path,
    *,
    use_gitignore: bool = False,
    use_default_exclusions: bool = False,
    gitignore_path: Optional[str | Path] = None,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    allow: Optional[List[str]] = None
) -> Structure
```

**Parameters:**
- `path` - directory path to scan
- `use_gitignore` - use .gitignore for filtering
- `use_default_exclusions` - use built-in exclusions
- `gitignore_path` - path to specific .gitignore file
- `include_patterns` - file patterns to include (supports * and ?)
- `exclude_patterns` - file patterns to exclude (supports * and ?)
- `allow` - patterns always allowed (highest priority)

**Returns:** `Structure` object with methods for formatting, saving and creating archives

### Structure Class

```python
# Convert to string
result.to_string(format_type: str = "tree", detailed: bool = False) -> str

# Save to file
result.to_file(
    path: str | Path,
    format_type: str = "tree",
    detailed: bool = False,
    encoding: str = "utf-8"
) -> Path

# Create ZIP archive
result.to_zip(path: str | Path) -> Path

# Get error list
result.get_errors() -> List[Tuple[Path, str]]

# Scan statistics
result.statistics -> dict
```

### Create ZIP from Text Function

```python
make_zip(
    input_file: str | Path,
    output_file: str | Path,
    format: str = "tree",
    encoding: str = "utf-8"
) -> Path
```

**Parameters:**
- `input_file` - path to text file with structure
- `output_file` - path for output ZIP file
- `format` - input file format ("tree", "list", "json", "csv", "xml")
- `encoding` - text file encoding

**Returns:** path to created ZIP file

**Supported input file formats:**
- `tree` - visual tree structure
- `list` - simple path list
- `json` - JSON structure (simple or full)
- `csv` - CSV table with paths
- `xml` - XML structure with node elements

### Available Formats

```python
from jai_folder_structure import get_formats

# Get list of all formats
formats = get_formats()
# ['csv', 'html', 'json', 'json-compact', 'list', 'markdown', 'tree', 'xml']
```

## Output Formats

### Tree (default)

**Brief mode:**
```
my_project/
├─ src/
│  ├─ main.py
│  └─ utils.py
├─ tests/
│  └─ test_main.py
└─ README.md
```

**Detailed mode:**
```
# Project: my_project
# Generated: 2025-06-21 10:30:00
# Scan time: 0.15s

my_project/          # 2 dirs, 4 files, 15.6 KB, 450 lines
├─ src/              # 2 files, 10.3 KB, 285 lines
│  ├─ main.py        # 7.2 KB, 180 lines
│  └─ utils.py       # 3.1 KB, 105 lines
├─ tests/            # 1 file, 2.8 KB, 95 lines
│  └─ test_main.py   # 2.8 KB, 95 lines
└─ README.md         # 2.5 KB, 70 lines
```

### JSON

**Brief mode:**
```json
{
  "root": {
    "name": "my_project",
    "path": "my_project/",
    "is_dir": true,
    "error": null,
    "children": []
  }
}
```
*Note: `children` array contains nested nodes*

**Detailed mode:**
```json
{
  "root": {
    "name": "my_project",
    "path": "my_project/",
    "is_dir": true,
    "size": 15974,
    "dirs": 2,
    "files": 4,
    "lines": 450,
    "error": null,
    "children": []
  },
  "metadata": {
    "created": "2025-06-21T10:30:00",
    "scan_time": 0.15,
    "errors_count": 0,
    "version": "1.0"
  }
}
```
*Note: `children` array contains nested nodes*

### Markdown

**Brief mode:**
```markdown
| Path | Type | Error |
|------|------|-------|
| my_project/ | dir | |
| my_project/src/ | dir | |
| my_project/src/main.py | file | |
| ⋮ | ⋮ | ⋮ |
```

**Detailed mode:**
```markdown
# Project Structure

**Project:** my_project  
**Generated:** 2025-06-21 10:30:00  
**Scan time:** 0.15s

## Files

| Path | Type | Size | Lines | Contents | Error |
|------|------|------|-------|----------|-------|
| my_project/ | dir | 15.6 KB | 450 | 2 dirs, 4 files | |
| my_project/src/ | dir | 10.3 KB | 285 | 2 files | |
| my_project/src/main.py | file | 7.2 KB | 180 | - | |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
```

### HTML

Generates complete HTML page with styling:
- Header with project information
- Tree representation in `<pre>` block
- Error highlighting in red
- Responsive design

### CSV

**Brief mode:**
```csv
path,is_dir,error
my_project/,true,
my_project/src/,true,
my_project/src/main.py,false,
⋮
```

**Detailed mode:**
```csv
path,is_dir,dirs,files,size,lines,error
my_project/,true,2,4,15974,450,
my_project/src/,true,0,2,10547,285,
my_project/src/main.py,false,,,7373,180,
⋮
```

### XML

**Brief mode:**
```xml
<folder_structure>
    <node name="my_project" path="my_project/" is_dir="true">
        <node name="src" path="my_project/src" is_dir="true">
            <node name="main.py" path="my_project/src/main.py" is_dir="false"/>
            <!-- more nodes -->
        </node>
        <!-- more nodes -->
    </node>
</folder_structure>
```

**Detailed mode:**
```xml
<folder_structure version="1.0" created="2025-06-21T10:30:00" scan_time="0.15" errors_count="0">
    <node name="my_project" path="my_project/" is_dir="true" dirs="2" files="4" size="15974" lines="450">
        <node name="src" path="my_project/src" is_dir="true" dirs="0" files="2" size="10547" lines="285">
            <node name="main.py" path="my_project/src/main.py" is_dir="false" size="7373" lines="180"/>
            <!-- more nodes -->
        </node>
        <!-- more nodes -->
    </node>
</folder_structure>
```

### List

**Brief mode:**
```
my_project/
my_project/src/
my_project/src/main.py
my_project/src/utils.py
⋮
```

**Detailed mode:**
```
# Project: my_project
# Generated: 2025-06-21 10:30:00
# Scan time: 0.15s

my_project/               # 2 dirs, 4 files, 15.6 KB, 450 lines
my_project/src/           # 2 files, 10.3 KB, 285 lines
my_project/src/main.py    # 7.2 KB, 180 lines
my_project/src/utils.py   # 3.1 KB, 105 lines
⋮
```

## Usage Examples

### Basic Usage

```python
from jai_folder_structure import get_structure

# Fast scan by default (without line counting)
result = get_structure("./project")

# Brief output - instant
print(result.to_string("tree"))

# Detailed output - auto-rescans on first call
print(result.to_string("tree", detailed=True))

# Repeated call - instant (data already loaded)
result.to_file("detailed.json", format_type="json", detailed=True)
```

### Saving Results

```python
result = get_structure("./project")

# Save in different formats
result.to_file("structure.txt")  # tree by default
result.to_file("structure.json", format_type="json")
result.to_file("structure.md", format_type="markdown", detailed=True)

# Auto-adds extensions
result.to_file("report", format_type="html")  # Saves as report.html

# Parent directories created automatically
result.to_file("output/docs/structure.md", format_type="markdown")

# Save with different detail levels
for detailed in [False, True]:
    suffix = "_detailed" if detailed else "_brief"
    result.to_file(f"structure{suffix}.txt", detailed=detailed)
```

### Working with Archives

#### Creating ZIP from Scanned Structure

```python
# Create ZIP from scanned structure
result = get_structure("./project", use_default_exclusions=True)
zip_path = result.to_zip("project_backup.zip")
print(f"Archive created: {zip_path}")

# Archive with filtering
result = get_structure(
    "./project",
    include_patterns=["*.py", "*.md"],
    use_gitignore=True
)
result.to_zip("python_files_only.zip")
```

#### Creating ZIP from Text Descriptions

```python
from jai_folder_structure import make_zip

# Create ZIP from text file with structure
result = get_structure("./project")
result.to_file("structure.txt", format_type="tree")
make_zip("structure.txt", "from_tree.zip", format="tree")

# Different input file formats supported
make_zip("structure.json", "from_json.zip", format="json")
make_zip("files.txt", "from_list.zip", format="list")
make_zip("structure.csv", "from_csv.zip", format="csv")
make_zip("structure.xml", "from_xml.zip", format="xml")
```

**Important:** When creating ZIP from text descriptions, all files are created empty. This is by design - only the directory structure is recreated, not the file contents.

**Input file format examples:**

**TREE format** (`structure.txt`):
```
project/
├─ src/
│  ├─ main.py
│  └─ utils.py
├─ tests/
│  └─ test_main.py
└─ README.md
```

**Important:** Elements are added to the nearest open folder with lower indentation level. A folder is considered "closed" when an element with indentation less than or equal to its indentation is encountered.

**Supported indent characters:** space, `│`, `├`, `└`, `─`, `-`, `–`, `—` or tab (don't mix with other characters).

**LIST format** (`files.txt`):
```
project/
project/src/
project/src/main.py
project/src/utils.py
project/tests/
project/tests/test_main.py
project/README.md
```

For other formats (JSON, CSV, XML) see "Output Formats" section above.

### Filtering

#### Basic Filtering

```python
# Python files only
result = get_structure(
    "./project",
    include_patterns=["*.py"]
)

# Exclude tests and cache
result = get_structure(
    "./project",
    exclude_patterns=["test_*", "__pycache__", "*.pyc"]
)
```

#### Using .gitignore

```python
# Use project's .gitignore
result = get_structure("./project", use_gitignore=True)

# Use specific .gitignore file
result = get_structure(
    "./project",
    use_gitignore=True,
    gitignore_path="/path/to/custom/.gitignore"
)

# Combine with allow patterns
result = get_structure(
    "./project",
    use_gitignore=True,
    allow=["important.log"]  # Show even if in .gitignore
)
```

#### Filter Priorities

1. **include_patterns** (highest priority) - If specified, ONLY files matching these patterns are shown
2. **allow** - Overrides exclusions (exclude/gitignore), but CANNOT show files filtered by include_patterns
3. **exclude_patterns + use_default_exclusions + use_gitignore** - Hides matching files/folders

**Decision logic:**
```
For each file/folder:
1. If include_patterns set AND file doesn't match → ❌ Hidden
2. If file matches allow patterns → ✅ Shown (overrides exclusions)
3. If file matches exclude/gitignore/default exclusions → ❌ Hidden
4. Otherwise → ✅ Shown
```

### Error Handling

```python
result = get_structure("./project")

# Check for errors
errors = result.get_errors()
if errors:
    print(f"Found {len(errors)} errors:")
    for path, error in errors:
        print(f"  {path}: {error}")

# Errors also shown in output
print(result.to_string("tree"))
# my_project/
# ├─ private_folder/  # Permission denied
# └─ normal_folder/
```

### Getting Statistics

```python
result = get_structure("./project")
stats = result.statistics

print(f"Total directories: {stats['total_dirs']}")
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size']:,} bytes")
print(f"Total lines of code: {stats['total_lines']:,}")
print(f"Scan time: {stats['scan_time']:.2f} sec")
print(f"Error count: {stats['errors_count']}")
```

## Supported Extensions for Line Counting

The library automatically counts lines for the following file types:

- **Python**: `.py`, `.pyi`, `.pyx`, `.pxd`, `.pyw`
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx`, `.vue`, `.svelte`
- **Web**: `.html`, `.htm`, `.xml`, `.xhtml`, `.css`, `.scss`, `.sass`, `.less`, `.styl`
- **Data**: `.json`, `.jsonc`, `.json5`, `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.config`, `.csv`, `.tsv`, `.psv`
- **Documentation**: `.md`, `.markdown`, `.rst`, `.adoc`, `.tex`, `.txt`, `.text`, `.log`
- **Shell**: `.sh`, `.bash`, `.zsh`, `.fish`, `.ksh`, `.ps1`, `.psm1`, `.psd1`, `.bat`, `.cmd`
- **C/C++**: `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.hh`
- **Java/JVM**: `.java`, `.kt`, `.kts`, `.scala`, `.groovy`
- **.NET**: `.cs`, `.fs`, `.fsx`, `.vb`
- **Go/Rust**: `.go`, `.rs`
- **Ruby/PHP**: `.rb`, `.rake`, `.gemspec`, `.php`
- **Other languages**: `.swift`, `.m`, `.mm`, `.pl`, `.pm`, `.pod`, `.lua`, `.r`, `.R`, `.jl`, `.sql`, `.pgsql`, `.mysql`, `.graphql`, `.gql`
- **Build/Config**: `.dockerfile`, `.dockerignore`, `.gitignore`, `.gitattributes`, `.gitmodules`, `.editorconfig`, `.prettierrc`, `.prettierignore`, `.eslintrc`, `.eslintignore`, `.babelrc`, `.browserslistrc`, `.env`, `.env.example`, `.env.local`, `.makefile`, `makefile`, `Makefile`, `.cmake`, `CMakeLists.txt`, `.pro`, `.pri`

## Default Exclusions

When using `use_default_exclusions=True`:
- **Version control**: `.git`, `.svn`, `.hg`, `.bzr`
- **Python**: `__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.coverage`, `htmlcov`, `.tox`, `*.egg-info`, `dist`, `build`
- **JavaScript/Node**: `node_modules`, `.npm`, `.yarn`, `.pnp.*`, `bower_components`
- **Virtual environments**: `.venv`, `venv`, `env`, `.env`, `virtualenv`
- **IDEs**: `.idea`, `.vscode`, `*.sublime-project`, `*.sublime-workspace`, `.project`, `.classpath`, `.settings`
- **OS-specific**: `.DS_Store`, `Thumbs.db`, `Desktop.ini`
- **Temporary**: `*.swp`, `*.swo`, `*~`, `*.tmp`, `*.temp`, `*.bak`, `*.backup`, `*.log`
- **Binary/compiled**: `*.exe`, `*.dll`, `*.so`, `*.dylib`, `*.class`, `*.o`, `*.a`

## Requirements

- Python 3.12+
- No external dependencies

## Known Limitations

- **Junction points and symbolic links**: the library follows them as regular directories. This may lead to file duplication in statistics or infinite recursion with circular links. For version 1.0, avoid scanning directories with circular symbolic links.
- **Case-sensitivity**: on Windows, files with names differing only in case (e.g., `File.txt` and `file.txt`) may overwrite each other when creating structure via `make_zip`.
- **Unicode in exclude patterns**: exclusion patterns may not work correctly for files with emoji and other Unicode characters in names.

## License

MIT License

---

🚀 **Created by [Claude Opus 4](https://claude.ai) • Reviewed by [Gemini 2.5 Pro](https://gemini.google.com), [ChatGPT o3](https://chat.openai.com), [DeepSeek R1](https://www.deepseek.com)**
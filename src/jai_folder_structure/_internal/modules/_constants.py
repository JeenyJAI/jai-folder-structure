"""Common constants for jai_folder_structure library."""

from typing import Set, FrozenSet

# ==============================================================================
# PATH AND SIZE CONSTANTS
# ==============================================================================

# Maximum width for path column in detailed output
MAX_PATH_WIDTH = 60

# Path length limits
MAX_PATH_LENGTH_WINDOWS = 260
MAX_PATH_LENGTH_UNIX = 4096

# Nesting depth limit for structures
MAX_NESTING_DEPTH = 100

# Path safety margin for ZIP operations
PATH_SAFETY_MARGIN = 50

# ==============================================================================
# FORMATTING CONSTANTS
# ==============================================================================

# Tree indentation size (spaces)
INDENT_SIZE = 3

# Date/time formats
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Tree drawing characters
TREE_PIPE = "│"
TREE_TEE = "├"
TREE_ELBOW = "└"
TREE_BRANCH = "─"

# ==============================================================================
# WINDOWS-SPECIFIC CONSTANTS
# ==============================================================================

# Reserved Windows file names
WINDOWS_RESERVED_NAMES: FrozenSet[str] = frozenset({
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
})

# Invalid characters for Windows file names
WINDOWS_INVALID_CHARS = '<>:"|?*'

# Minimum printable character code
MIN_PRINTABLE_CHAR_CODE = 32

# ==============================================================================
# ERROR CODES
# ==============================================================================

# errno code for "No space left on device"
ERRNO_NO_SPACE_LEFT = 28

# ==============================================================================
# FILE EXTENSIONS
# ==============================================================================

# Text file extensions for line counting
TEXT_EXTENSIONS: Set[str] = {
    # Python
    '.py', '.pyi', '.pyx', '.pxd', '.pyw',
    
    # Web
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    '.html', '.htm', '.xml', '.xhtml',
    '.css', '.scss', '.sass', '.less', '.styl',
    
    # Data formats
    '.json', '.jsonc', '.json5',
    '.yml', '.yaml',
    '.toml', '.ini', '.cfg', '.conf', '.config',
    '.csv', '.tsv', '.psv',
    
    # Documentation
    '.md', '.markdown', '.rst', '.adoc', '.tex',
    '.txt', '.text', '.log',
    
    # Shell/Scripts
    '.sh', '.bash', '.zsh', '.fish', '.ksh',
    '.bat', '.cmd', '.ps1', '.psm1', '.psd1',
    
    # Programming languages
    '.java', '.kt', '.kts', '.scala', '.groovy',
    '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx', '.hh',
    '.cs', '.fs', '.fsx', '.vb',
    '.rs', '.go', '.swift', '.m', '.mm',
    '.rb', '.rake', '.gemspec',
    '.php', '.pl', '.pm', '.pod',
    '.lua', '.r', '.R', '.jl',
    '.sql', '.pgsql', '.mysql',
    '.graphql', '.gql',
    
    # Config files
    '.dockerfile', '.dockerignore',
    '.gitignore', '.gitattributes', '.gitmodules',
    '.editorconfig', '.prettierrc', '.prettierignore',
    '.eslintrc', '.eslintignore',
    '.babelrc', '.browserslistrc',
    '.env', '.env.example', '.env.local',
    
    # Other
    '.makefile', 'makefile', 'Makefile',
    '.cmake', 'CMakeLists.txt',
    '.pro', '.pri',  # Qt project files
}

# ==============================================================================
# DEFAULT PATTERNS
# ==============================================================================

# Default exclusion patterns
DEFAULT_EXCLUSIONS = [
    # Version control
    '.git',
    '.svn',
    '.hg',
    '.bzr',
    
    # Python
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.coverage',
    'htmlcov',
    '.tox',
    '*.egg-info',
    'dist',
    'build',
    
    # JavaScript/Node
    'node_modules',
    '.npm',
    '.yarn',
    '.pnp.*',
    'bower_components',
    
    # Virtual environments
    '.venv',
    'venv',
    'env',
    '.env',
    'virtualenv',
    
    # IDEs
    '.idea',
    '.vscode',
    '*.sublime-project',
    '*.sublime-workspace',
    '.project',
    '.classpath',
    '.settings',
    
    # OS-specific
    '.DS_Store',
    'Thumbs.db',
    'Desktop.ini',
    
    # Temporary files
    '*.swp',
    '*.swo',
    '*~',
    '*.tmp',
    '*.temp',
    '*.bak',
    '*.backup',
    '*.log',
    
    # Binary/compiled
    '*.exe',
    '*.dll',
    '*.so',
    '*.dylib',
    '*.class',
    '*.o',
    '*.a',
]
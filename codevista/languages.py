"""Language definitions and GitHub-style colors."""

LANG_MAP = {
    '.py': 'Python', '.pyw': 'Python', '.pyx': 'Cython', '.pxd': 'Cython',
    '.js': 'JavaScript', '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.ts': 'TypeScript', '.tsx': 'TypeScript', '.mts': 'TypeScript',
    '.rb': 'Ruby', '.rake': 'Ruby', '.erb': 'Ruby',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java', '.jar': 'Java',
    '.kt': 'Kotlin', '.kts': 'Kotlin',
    '.scala': 'Scala',
    '.swift': 'Swift',
    '.c': 'C', '.h': 'C',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.hxx': 'C++',
    '.cs': 'C#',
    '.php': 'PHP', '.phtml': 'PHP',
    '.html': 'HTML', '.htm': 'HTML',
    '.css': 'CSS', '.scss': 'SCSS', '.sass': 'SCSS', '.less': 'Less',
    '.json': 'JSON', '.jsonl': 'JSON',
    '.xml': 'XML', '.xsl': 'XML', '.xslt': 'XML', '.xsd': 'XML',
    '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML',
    '.md': 'Markdown', '.mdx': 'Markdown',
    '.sh': 'Shell', '.bash': 'Shell', '.zsh': 'Shell', '.fish': 'Shell',
    '.sql': 'SQL',
    '.r': 'R', '.R': 'R',
    '.lua': 'Lua',
    '.dart': 'Dart',
    '.ex': 'Elixir', '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hs': 'Haskell',
    '.ml': 'OCaml', '.mli': 'OCaml',
    '.clj': 'Clojure', '.cljs': 'Clojure',
    '.pl': 'Perl', '.pm': 'Perl',
    '.vim': 'Vim script',
    '.dockerfile': 'Dockerfile',
    '.graphql': 'GraphQL', '.gql': 'GraphQL',
    '.proto': 'Protocol Buffers',
    '.tf': 'HCL', '.tfvars': 'HCL',
    '.vue': 'Vue', '.svelte': 'Svelte',
    '.makefile': 'Makefile',
    '.cmake': 'CMake',
    '.gradle': 'Gradle',
    '.ini': 'INI', '.cfg': 'INI', '.conf': 'INI',
    '.txt': 'Text',
    '.csv': 'CSV',
    '.lock': 'Lockfile',
    '.pyi': 'Python',
}

# GitHub-inspired colors
LANG_COLORS = {
    'Python': '#3572A5',
    'JavaScript': '#f1e05a',
    'TypeScript': '#3178c6',
    'Ruby': '#701516',
    'Go': '#00ADD8',
    'Rust': '#dea584',
    'Java': '#b07219',
    'Kotlin': '#A97BFF',
    'Swift': '#F05138',
    'C': '#555555',
    'C++': '#f34b7d',
    'C#': '#178600',
    'PHP': '#4F5D95',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'SCSS': '#c6538c',
    'Less': '#1d365d',
    'JSON': '#292929',
    'YAML': '#cb171e',
    'TOML': '#9c4221',
    'Markdown': '#083fa1',
    'Shell': '#89e051',
    'SQL': '#e38c00',
    'R': '#198CE7',
    'Lua': '#000080',
    'Dart': '#00B4AB',
    'Elixir': '#6e4a7e',
    'Haskell': '#5e5086',
    'Vue': '#41b883',
    'Svelte': '#ff3e00',
    'Dockerfile': '#384d54',
    'GraphQL': '#e535ab',
    'Makefile': '#427819',
    'CMake': '#064f8c',
    'Text': '#999999',
}

IGNORED_EXTENSIONS = {
    '.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.dylib',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.exe', '.msi', '.dmg', '.app', '.deb', '.rpm',
    '.sqlite', '.db', '.bak',
}

def detect_language(filepath):
    """Detect language from file extension."""
    import os
    name = os.path.basename(filepath).lower()
    # Special filenames
    if name == 'dockerfile':
        return 'Dockerfile'
    if name == 'makefile' or name == 'gnumakefile':
        return 'Makefile'
    if name == 'cmakelists.txt':
        return 'CMake'
    if name == '.gitignore' or name == '.dockerignore':
        return 'Config'
    _, ext = os.path.splitext(filepath)
    return LANG_MAP.get(ext.lower(), None)

def get_lang_color(lang):
    return LANG_COLORS.get(lang, '#999999')

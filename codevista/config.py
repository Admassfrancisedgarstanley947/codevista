"""Configuration and ignore patterns."""

import os

DEFAULT_CONFIG = {
    'max_file_size': 1_000_000,  # 1MB
    'max_depth': None,
    'include_hidden': False,
    'include_git': True,
    'include_vendored': False,
    'binary_extensions': {
        '.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.dylib',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp',
        '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.ttf', '.otf', '.woff', '.woff2', '.eot',
        '.exe', '.msi', '.dmg', '.app', '.deb', '.rpm',
        '.sqlite', '.db', '.woff', '.eot',
        '.wasm', '.nib', '.storyboard', '.xib',
    },
    'vendored_dirs': {
        'node_modules', 'vendor', '.venv', 'venv', 'env',
        '__pycache__', '.tox', '.eggs', '*.egg-info',
        'dist', 'build', '.next', '.nuxt', 'target',
        '.mypy_cache', '.pytest_cache', '.ruff_cache',
    },
    'ignore_patterns': [
        '.git', '.svn', '.hg', '.codevistaignore',
    ],
}


def load_config(project_path):
    """Load .codevistaignore patterns from project root."""
    ignore_file = os.path.join(project_path, '.codevistaignore')
    patterns = set(DEFAULT_CONFIG['ignore_patterns'])
    if os.path.isfile(ignore_file):
        with open(ignore_file, 'r', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    return patterns


def should_ignore(filepath, project_path, ignore_patterns=None):
    """Check if a file/directory should be ignored."""
    import os
    rel = os.path.relpath(filepath, project_path)
    parts = rel.replace('\\', '/').split('/')
    
    cfg = DEFAULT_CONFIG
    if ignore_patterns is None:
        ignore_patterns = load_config(project_path)
    
    for part in parts:
        if part in ignore_patterns:
            return True
        if part in cfg['vendored_dirs']:
            return True
        if part.startswith('.') and not cfg['include_hidden']:
            return True
    
    _, ext = os.path.splitext(filepath)
    if ext.lower() in cfg['binary_extensions']:
        return True
    
    return False

"""Utility functions for file discovery, complexity calculation, and color schemes."""

import os
import re
import hashlib

from .config import should_ignore, DEFAULT_CONFIG


def discover_files(project_path, max_depth=None, ignore_patterns=None):
    """Walk directory tree and return list of source files."""
    files = []
    for root, dirs, filenames in os.walk(project_path):
        # Filter dirs in-place
        dirs[:] = sorted([d for d in dirs if not should_ignore(
            os.path.join(root, d), project_path, ignore_patterns)])
        
        if max_depth is not None:
            rel_depth = os.path.relpath(root, project_path).replace('\\', '/').count('/')
            if rel_depth > max_depth:
                dirs[:] = []
                continue
        
        for fname in sorted(filenames):
            fpath = os.path.join(root, fname)
            if should_ignore(fpath, project_path, ignore_patterns):
                continue
            if os.path.getsize(fpath) > DEFAULT_CONFIG['max_file_size']:
                continue
            files.append(fpath)
    return files


def read_file_safe(filepath):
    """Read file contents with encoding fallback."""
    for enc in ('utf-8', 'utf-8-sig', 'latin-1', 'ascii'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ''


def count_lines(content):
    """Count total, code, blank, and comment lines."""
    lines = content.split('\n')
    total = max(len(lines) - (1 if lines and lines[-1] == '' else 0), 0)
    blank = sum(1 for l in lines if not l.strip())
    comment = sum(1 for l in lines if is_comment_line(l))
    code = total - blank - comment
    return {'total': total, 'code': code, 'blank': blank, 'comment': comment}


def is_comment_line(line):
    """Simple comment detection for common languages."""
    s = line.strip()
    if not s:
        return False
    return (s.startswith('#') or s.startswith('//') or 
            s.startswith('/*') or s.startswith('*') or s.startswith('--') or
            s.startswith('<!--') or s.startswith('%'))


def cyclomatic_complexity(content):
    """Calculate cyclomatic complexity of a code block."""
    keywords = (
        r'\bif\b', r'\belif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
        r'\bcase\b', r'\bcatch\b', r'\bexcept\b', r'\bfinally\b',
        r'\bwith\b', r'\band\b', r'\bor\b', r'\bwhen\b',
    )
    pattern = '|'.join(keywords)
    count = len(re.findall(pattern, content))
    # Subtract function/class defs since they add 1 for structure
    func_count = len(re.findall(r'\bdef\b|\bfunction\b|\bfn\b|\bfunc\b|\b->', content))
    return max(count - func_count + 1, 1)


def extract_imports(content, language):
    """Extract import statements from code."""
    imports = []
    if language in ('Python', 'Cython'):
        imports = re.findall(r'^(?:from|import)\s+([^\s;]+)', content, re.MULTILINE)
    elif language in ('JavaScript', 'TypeScript', 'Vue', 'Svelte'):
        imports = re.findall(r'(?:import|require)\s*[\(\'"]?([^\'")\s;]+)', content)
    elif language in ('Go',):
        imports = re.findall(r'import\s+"([^"]+)"', content)
    elif language in ('Java', 'Kotlin', 'C#'):
        imports = re.findall(r'import\s+([^\s;]+)', content)
    elif language in ('C', 'C++'):
        imports = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
    elif language in ('Ruby',):
        imports = re.findall(r'(?:require|gem)\s+[\'"]([^\'"]+)[\'"]', content)
    return imports


def normalize_import(imp):
    """Normalize import to base module name."""
    return imp.split('.')[0].split('/')[0].lower()


def compute_file_hash(content):
    """Hash file content for duplication detection."""
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()


def normalize_for_duplication(content):
    """Normalize code for duplication detection (remove strings, comments, whitespace)."""
    # Remove strings
    content = re.sub(r'(["\'])(?:(?!\1).)*\1', '""', content)
    # Remove comments
    content = re.sub(r'#[^\n]*', '', content)
    content = re.sub(r'//[^\n]*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Collapse whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    return content


def block_hash(content, block_size=6):
    """Create hashes of code blocks for duplication detection."""
    lines = content.split('\n')
    blocks = []
    for i in range(len(lines) - block_size + 1):
        block = '\n'.join(lines[i:i+block_size])
        normalized = normalize_for_duplication(block)
        if len(normalized) > 50:  # Skip trivial blocks
            blocks.append(hashlib.md5(normalized.encode()).hexdigest())
    return blocks


# Color schemes for the report
COLORS = {
    'bg': '#0f0e17',
    'surface': '#1a1a2e',
    'surface2': '#232340',
    'text': '#fffffe',
    'text2': '#a7a9be',
    'primary': '#7f5af0',
    'primary2': '#2cb67d',
    'accent': '#e53170',
    'warning': '#ff8906',
    'info': '#72757e',
    'gradient_start': '#7f5af0',
    'gradient_end': '#2cb67d',
}

THEMES = {
    'dark': COLORS,
    'light': {
        'bg': '#fffffe', 'surface': '#f0f0f5', 'surface2': '#e8e8f0',
        'text': '#0f0e17', 'text2': '#52525b',
        'primary': '#7f5af0', 'primary2': '#2cb67d',
        'accent': '#e53170', 'warning': '#ff8906', 'info': '#72757e',
        'gradient_start': '#7f5af0', 'gradient_end': '#2cb67d',
    }
}

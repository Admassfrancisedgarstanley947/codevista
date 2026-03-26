"""Core analyzer — language detection, complexity, duplication, framework detection."""

import os
from collections import Counter, defaultdict

from .languages import detect_language, get_lang_color
from .utils import (
    discover_files, read_file_safe, count_lines, cyclomatic_complexity,
    extract_imports, normalize_import, block_hash, compute_file_hash,
    normalize_for_duplication, is_comment_line,
)
from .config import load_config
from .security import scan_file
from .dependencies import find_dependencies, detect_circular_imports
from .git_analysis import full_git_analysis


def analyze_project(project_path, max_depth=None, include_git=True):
    """Full analysis of a project."""
    project_path = os.path.abspath(project_path)
    ignore_patterns = load_config(project_path)
    
    # Discover files
    files = discover_files(project_path, max_depth, ignore_patterns)
    
    # Per-file analysis
    file_data = []
    import_graph = defaultdict(set)
    all_blocks = defaultdict(list)  # block_hash -> [filepath]
    lang_stats = Counter()
    framework_markers = Counter()
    file_hashes = defaultdict(list)
    total_lines = {'code': 0, 'comment': 0, 'blank': 0, 'total': 0}
    security_issues = []
    complexities = []
    
    for fpath in files:
        lang = detect_language(fpath)
        if lang is None:
            continue
        
        content = read_file_safe(fpath)
        if not content:
            continue
        
        rel_path = os.path.relpath(fpath, project_path)
        lc = count_lines(content)
        cc = cyclomatic_complexity(content)
        imports = extract_imports(content, lang)
        file_size = os.path.getsize(fpath)
        
        # Collect metrics
        total_lines['code'] += lc['code']
        total_lines['comment'] += lc['comment']
        total_lines['blank'] += lc['blank']
        total_lines['total'] += lc['total']
        lang_stats[lang] += lc['total']
        complexities.append(cc)
        
        # Import graph
        norm_name = rel_path.replace('\\', '/').replace('/', '.')
        for imp in imports:
            import_graph[norm_name].add(normalize_import(imp))
        
        # Duplication detection
        fh = compute_file_hash(normalize_for_duplication(content))
        file_hashes[fh].append(rel_path)
        
        blocks = block_hash(content)
        for bh in blocks:
            all_blocks[bh].append(rel_path)
        
        # Security
        issues = scan_file(fpath, content)
        security_issues.extend(issues)
        
        file_data.append({
            'path': rel_path,
            'language': lang,
            'color': get_lang_color(lang),
            'lines': lc,
            'complexity': cc,
            'size': file_size,
            'imports': imports[:20],
        })
    
    # Detect frameworks
    frameworks = detect_frameworks(project_path)
    
    # Find duplicates
    duplicates = []
    seen_blocks = set()
    for bh, paths in all_blocks.items():
        if len(paths) > 1 and bh not in seen_blocks:
            # Deduplicate (same pair might appear multiple times)
            key = tuple(sorted(set(paths)))
            if len(key) > 1:
                seen_blocks.add(bh)
                duplicates.append({'files': list(set(paths)), 'type': 'block'})
    
    # Exact file duplicates
    for fh, paths in file_hashes.items():
        if len(paths) > 1:
            duplicates.append({'files': paths, 'type': 'exact'})
    
    # Circular deps
    circular = detect_circular_imports(dict(import_graph))
    
    # Dependencies
    deps, pkg_manager = find_dependencies(project_path)
    
    # Git
    git_data = full_git_analysis(project_path) if include_git else None
    
    # Directory structure
    dir_structure = build_dir_tree(file_data, project_path)
    
    return {
        'project_name': os.path.basename(project_path),
        'project_path': project_path,
        'files': file_data,
        'total_files': len(file_data),
        'total_lines': total_lines,
        'languages': dict(lang_stats.most_common()),
        'frameworks': frameworks,
        'avg_complexity': sum(complexities) / len(complexities) if complexities else 0,
        'max_complexity': max(complexities) if complexities else 0,
        'duplicates': duplicates[:50],
        'security_issues': security_issues,
        'circular_deps': circular,
        'dependencies': deps,
        'package_manager': pkg_manager,
        'import_graph': dict(import_graph),
        'git': git_data,
        'dir_tree': dir_structure,
    }


def detect_frameworks(project_path):
    """Detect frameworks from config files and patterns."""
    frameworks = []
    checkers = [
        ('package.json', [
            ('react', 'React'), ('vue', 'Vue'), ('angular', 'Angular'),
            ('next', 'Next.js'), ('nuxt', 'Nuxt'), ('svelte', 'Svelte'),
            ('express', 'Express'), ('fastify', 'Fastify'), ('koa', 'Koa'),
            ('typescript', 'TypeScript'), ('tailwindcss', 'Tailwind CSS'),
            ('vite', 'Vite'), ('webpack', 'Webpack'), ('eslint', 'ESLint'),
        ]),
        ('requirements.txt', [
            ('django', 'Django'), ('flask', 'Flask'), ('fastapi', 'FastAPI'),
            ('starlette', 'Starlette'), ('requests', 'Requests'),
            ('celery', 'Celery'), ('scikit-learn', 'scikit-learn'),
            ('tensorflow', 'TensorFlow'), ('pytorch', 'PyTorch'),
            ('pandas', 'Pandas'), ('numpy', 'NumPy'),
            ('pytest', 'pytest'), ('selenium', 'Selenium'),
        ]),
    ]
    
    import json
    for fname, patterns in checkers:
        fpath = os.path.join(project_path, fname)
        if not os.path.isfile(fpath):
            continue
        content = read_file_safe(fpath).lower()
        for pattern, name in patterns:
            if pattern in content:
                frameworks.append(name)
    
    # Check for extra markers
    if os.path.isfile(os.path.join(project_path, 'manage.py')):
        frameworks.append('Django')
    if os.path.isfile(os.path.join(project_path, 'next.config.js')) or os.path.isfile(os.path.join(project_path, 'next.config.mjs')):
        frameworks.append('Next.js')
    if os.path.isfile(os.path.join(project_path, 'angular.json')):
        frameworks.append('Angular')
    if os.path.isfile(os.path.join(project_path, 'Cargo.toml')):
        frameworks.append('Rust')
    
    return list(set(frameworks))


def build_dir_tree(file_data, project_path):
    """Build directory tree from file data."""
    tree = {}
    for f in file_data:
        parts = f['path'].replace('\\', '/').split('/')
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = f['lines']['total']
    return tree

"""Dependency parsing and analysis."""

import os
import re
import json
from urllib.request import urlopen, Request
from urllib.error import URLError


def parse_requirements(filepath):
    """Parse requirements.txt."""
    deps = []
    with open(filepath, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('-'):
                continue
            # Handle extras, version specifiers
            m = re.match(r'^([a-zA-Z0-9_-]+)\s*(.*)', line)
            if m:
                deps.append({'name': m.group(1), 'spec': m.group(2) or '*'})
    return deps


def parse_package_json(filepath):
    """Parse package.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], [], []
    
    all_deps = []
    for section in ('dependencies', 'devDependencies', 'peerDependencies'):
        for name, ver in data.get(section, {}).items():
            all_deps.append({'name': name, 'spec': ver, 'section': section})
    return all_deps


def parse_pyproject_toml(filepath):
    """Basic pyproject.toml parser for dependencies."""
    deps = []
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        # Find [project.dependencies] or [tool.poetry.dependencies]
        in_deps = False
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('['):
                if 'dependencies' in stripped and ('project' in stripped or 'poetry' in stripped):
                    in_deps = True
                else:
                    in_deps = False
                continue
            if in_deps and stripped:
                m = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', stripped)
                if m:
                    deps.append({'name': m.group(1), 'spec': m.group(2)})
    except Exception:
        pass
    return deps


def parse_cargo_toml(filepath):
    """Parse Cargo.toml."""
    deps = []
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
    in_deps = False
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('['):
            in_deps = 'dependencies' in stripped
            continue
        if in_deps and stripped:
            m = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', stripped)
            if m:
                deps.append({'name': m.group(1), 'spec': m.group(2)})
    return deps


def parse_go_mod(filepath):
    """Parse go.mod."""
    deps = []
    with open(filepath, 'r', errors='ignore') as f:
        in_deps = False
        for line in f:
            if line.strip().startswith('require ('):
                in_deps = True
                continue
            if in_deps:
                if line.strip() == ')':
                    break
                parts = line.strip().split()
                if len(parts) >= 2:
                    deps.append({'name': parts[0], 'spec': parts[1]})
            elif line.strip().startswith('require '):
                parts = line.strip().split()
                if len(parts) >= 3:
                    deps.append({'name': parts[1], 'spec': parts[2]})
    return deps


def find_dependencies(project_path):
    """Find and parse all dependency files."""
    deps = []
    pkg_manager = None
    
    # Python
    for fname in ('requirements.txt', 'requirements-dev.txt', 'requirements/prod.txt'):
        fpath = os.path.join(project_path, fname)
        if os.path.isfile(fpath):
            pkg_manager = 'pip'
            deps.extend(parse_requirements(fpath))
    
    pyproject = os.path.join(project_path, 'pyproject.toml')
    if os.path.isfile(pyproject):
        pkg_manager = pkg_manager or 'pip'
        deps.extend(parse_pyproject_toml(pyproject))
    
    # Node
    pkg_json = os.path.join(project_path, 'package.json')
    if os.path.isfile(pkg_json):
        pkg_manager = 'npm'
        deps.extend(parse_package_json(pkg_json))
    
    # Rust
    cargo = os.path.join(project_path, 'Cargo.toml')
    if os.path.isfile(cargo):
        pkg_manager = 'cargo'
        deps.extend(parse_cargo_toml(cargo))
    
    # Go
    gomod = os.path.join(project_path, 'go.mod')
    if os.path.isfile(gomod):
        pkg_manager = 'go'
        deps.extend(parse_go_mod(gomod))
    
    return deps, pkg_manager


def detect_circular_imports(import_graph):
    """Detect circular dependencies in import graph."""
    visited = set()
    path = set()
    cycles = []
    
    def dfs(node, current_path):
        if node in current_path:
            cycle_start = list(current_path).index(node)
            cycle = list(current_path)[cycle_start:] + [node]
            cycles.append(cycle)
            return
        if node in visited:
            return
        visited.add(node)
        new_path = current_path | {node}
        for dep in import_graph.get(node, []):
            dfs(dep, new_path)
    
    for node in list(import_graph.keys())[:500]:  # Limit search
        dfs(node, set())
    
    return cycles[:20]  # Cap at 20 cycles


def check_outdated(dep_name, current_spec, pkg_manager='pip'):
    """Check if a dependency is outdated using free public APIs."""
    try:
        if pkg_manager in ('pip', 'poetry'):
            url = f'https://pypi.org/pypi/{dep_name}/json'
            req = Request(url, headers={'User-Agent': 'CodeVista/0.1'})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            latest = data['info']['version']
            return {'name': dep_name, 'current': current_spec, 'latest': latest}
        elif pkg_manager in ('npm', 'yarn'):
            url = f'https://registry.npmjs.org/{dep_name}'
            req = Request(url, headers={'User-Agent': 'CodeVista/0.1'})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            latest = data.get('dist-tags', {}).get('latest', 'unknown')
            return {'name': dep_name, 'current': current_spec, 'latest': latest}
    except (URLError, OSError, KeyError, json.JSONDecodeError):
        return None
    return None

"""Git analysis — contributions, stats, history."""

import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, '.git'))


def git_command(path, *args):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + list(args),
            cwd=path, capture_output=True, text=True, timeout=30,
            encoding='utf-8', errors='replace'
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ''


def get_authors(path, limit=50):
    """Get commit stats per author."""
    output = git_command(path, 'log', '--format=%aN', '-1000')
    if not output:
        return []
    authors = Counter(output.split('\n'))
    return [{'name': name, 'commits': count} for name, count in authors.most_common(limit)]


def get_commit_stats(path):
    """Get lines added/removed per commit."""
    output = git_command(path, 'log', '--shortstat', '--format=%H', '-500')
    if not output:
        return []
    stats = []
    blocks = output.split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        sha = lines[0][:8] if lines else ''
        for line in lines[1:]:
            m = re.search(r'(\d+) insertion', line)
            added = int(m.group(1)) if m else 0
            m = re.search(r'(\d+) deletion', line)
            removed = int(m.group(1)) if m else 0
            stats.append({'sha': sha, 'added': added, 'removed': removed})
    return stats


def get_contribution_heatmap(path, year=None):
    """Get contribution counts per day for the last year."""
    if year is None:
        year = str(datetime.now().year)
    output = git_command(path, 'log', '--since', f'{year}-01-01', '--format=%ad', '--date=short')
    if not output:
        return {}
    return Counter(output.split('\n'))


def get_most_active_files(path, limit=20):
    """Get files with most commits."""
    output = git_command(path, 'log', '--name-only', '--format=', '-1000')
    if not output:
        return []
    files = Counter(f for f in output.split('\n') if f.strip())
    return [{'file': name, 'commits': count} for name, count in files.most_common(limit)]


def get_branch_info(path):
    """Get branch info."""
    current = git_command(path, 'rev-parse', '--abbrev-ref', 'HEAD')
    branches = git_command(path, 'branch', '-a')
    branch_list = [b.strip().lstrip('* ') for b in branches.split('\n') if b.strip()] if branches else []
    return {
        'current': current or 'unknown',
        'count': len(branch_list),
        'branches': branch_list[:20],
    }


def get_total_commits(path):
    output = git_command(path, 'rev-list', '--count', 'HEAD')
    return int(output) if output.isdigit() else 0


def get_first_last_commit(path):
    first = git_command(path, 'log', '--reverse', '--format=%ad', '--date=short', '-1')
    last = git_command(path, 'log', '--format=%ad', '--date=short', '-1')
    return {'first': first or 'unknown', 'last': last or 'unknown'}


def full_git_analysis(path):
    """Run full git analysis."""
    if not is_git_repo(path):
        return None
    
    return {
        'authors': get_authors(path),
        'commit_stats': get_commit_stats(path),
        'heatmap': get_contribution_heatmap(path),
        'active_files': get_most_active_files(path),
        'branches': get_branch_info(path),
        'total_commits': get_total_commits(path),
        'date_range': get_first_last_commit(path),
    }

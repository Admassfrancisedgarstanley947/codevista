"""Team metrics — developer productivity and collaboration analysis.

Lines of code per author, commit frequency, files touched, bus factor,
code ownership distribution, review coverage, pair programming detection,
time zone distribution, active/inactive contributor detection, and
new contributor onboarding complexity.
"""

import os
import re
import sys
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from .git_analysis import (git_command, is_git_repo, get_authors,
                               get_author_emails, get_commit_stats,
                               get_commit_frequency, get_contribution_by_weekday,
                               get_contribution_by_hour, get_most_active_files,
                               get_file_coauthorship, get_total_commits,
                               get_active_developers, get_commit_message_stats)
except ImportError:
    from git_analysis import (git_command, is_git_repo, get_authors,
                              get_author_emails, get_commit_stats,
                              get_commit_frequency, get_contribution_by_weekday,
                              get_contribution_by_hour, get_most_active_files,
                              get_file_coauthorship, get_total_commits,
                              get_active_developers, get_commit_message_stats)


def analyze_team(path: str) -> Dict[str, Any]:
    """Run complete team metrics analysis on a git repository."""
    if not is_git_repo(path):
        return {'error': 'Not a git repository'}

    authors = get_authors(path)
    if not authors:
        return {'error': 'No commits found'}

    total_commits = get_total_commits(path)

    # Author LOC analysis
    author_loc = _get_author_loc(path, authors)

    # Author file stats
    author_files = _get_author_files(path, authors)

    # Commit frequency per author
    author_frequency = _get_author_commit_frequency(path)

    # Active/inactive detection
    active_devs = get_active_developers(path, days=90)
    inactive_devs = [a for a in authors if a['name'] not in
                     {d['name'] for d in active_devs}]

    # Bus factor
    bus_factor = _calculate_bus_factor_detailed(authors, total_commits)

    # Code ownership distribution
    ownership = _compute_ownership(authors, total_commits)

    # Review coverage estimate
    review_coverage = _estimate_review_coverage(path)

    # Pair programming detection (co-authored commits)
    pair_programming = _detect_pair_programming(path)

    # Time zone distribution
    timezone_dist = _analyze_timezone_distribution(path)

    # Onboarding complexity
    onboarding = _compute_onboarding_complexity(path, author_files)

    # Commit size per author
    author_commit_sizes = _get_author_commit_sizes(path, authors)

    # Work pattern analysis
    work_patterns = _analyze_work_patterns(path)

    # Code review collaboration
    collaboration = _analyze_collaboration(path, authors, author_files)

    # Message quality per author
    author_msg_quality = _get_author_message_quality(path, authors)

    return {
        'total_commits': total_commits,
        'total_contributors': len(authors),
        'authors': authors,
        'author_loc': author_loc,
        'author_files': author_files,
        'author_frequency': author_frequency,
        'author_commit_sizes': author_commit_sizes,
        'author_msg_quality': author_msg_quality,
        'active_developers': active_devs,
        'inactive_developers': inactive_devs,
        'bus_factor': bus_factor,
        'ownership': ownership,
        'review_coverage': review_coverage,
        'pair_programming': pair_programming,
        'timezone_distribution': timezone_dist,
        'onboarding': onboarding,
        'work_patterns': work_patterns,
        'collaboration': collaboration,
    }


def format_team_terminal(team_data: Dict[str, Any]) -> str:
    """Format team analysis for terminal output."""
    if 'error' in team_data:
        return f"❌ {team_data['error']}\n"

    lines = []
    lines.append(f"\n{'═'*60}")
    lines.append(f"  👥 CodeVista Team Analysis")
    lines.append(f"{'═'*60}")

    lines.append(f"\n  📊 Overview")
    lines.append(f"  {'─'*45}")
    lines.append(f"  Total Commits:       {team_data['total_commits']:,}")
    lines.append(f"  Contributors:        {team_data['total_contributors']}")
    lines.append(f"  Active (90d):        {len(team_data['active_developers'])}")
    lines.append(f"  Inactive (90d):      {len(team_data['inactive_developers'])}")

    # Bus factor
    bf = team_data['bus_factor']
    bf_color = '🔴' if bf['factor'] <= 1 else '🟡' if bf['factor'] <= 2 else '🟢'
    lines.append(f"  {bf_color} Bus Factor:          {bf['factor']} "
                 f"({bf['key_authors'][:3]})")

    # Author LOC table
    lines.append(f"\n  📝 Lines of Code per Author")
    lines.append(f"  {'─'*60}")
    lines.append(f"  {'Author':<25s} {'Added':>8s} {'Removed':>8s} {'Net':>8s} {'Commits':>8s}")
    lines.append(f"  {'─'*60}")
    for a in team_data['author_loc'][:15]:
        name = a['name'][:24]
        lines.append(
            f"  {name:<25s} {a['added']:>8,} {a['removed']:>8,} "
            f"{a['net']:>+8,} {a['commits']:>8d}"
        )

    # Commit frequency
    lines.append(f"\n  📅 Commit Frequency (commits per day)")
    lines.append(f"  {'─'*45}")
    for a in team_data['author_frequency'][:15]:
        name = a['name'][:24]
        bar_len = min(int(a['commits_per_day'] * 20), 30)
        bar = '█' * bar_len
        lines.append(f"  {name:<25s} {a['commits_per_day']:.2f}/day  {bar}")

    # Files touched
    lines.append(f"\n  📂 Files Touched per Author")
    lines.append(f"  {'─'*45}")
    for a in team_data['author_files'][:15]:
        name = a['name'][:24]
        bar_len = min(int(a['files'] / max(team_data['author_files'][0]['files'], 1) * 30), 30)
        bar = '█' * bar_len
        lines.append(f"  {name:<25s} {a['files']:>5d} files  {bar}")

    # Ownership distribution (pie chart data)
    lines.append(f"\n  🥧 Code Ownership Distribution")
    lines.append(f"  {'─'*45}")
    for o in team_data['ownership']:
        pct_str = f"{o['percentage']:.1f}%"
        bar_len = int(o['percentage'] / 3)
        bar = '█' * bar_len
        lines.append(f"  {o['name']:<25s} {pct_str:>6s}  {bar}")

    # Review coverage
    rc = team_data['review_coverage']
    lines.append(f"\n  🔍 Review Coverage Estimate")
    lines.append(f"  {'─'*45}")
    lines.append(f"  Commits with review keywords: {rc['reviewed']}")
    lines.append(f"  Total commits analyzed:       {rc['total']}")
    lines.append(f"  Review coverage:              {rc['coverage_pct']:.1f}%")
    if rc['coverage_pct'] < 50:
        lines.append(f"  ⚠️  Low review coverage — consider mandating PR reviews")

    # Pair programming
    pp = team_data['pair_programming']
    lines.append(f"\n  👯 Pair Programming Detection")
    lines.append(f"  {'─'*45}")
    lines.append(f"  Co-authored commits:  {pp['coauthored_count']}")
    lines.append(f"  Co-author pairs:      {len(pp['pairs'])}")
    if pp['pairs']:
        lines.append(f"  Top pairs:")
        for pair, count in pp['pairs'][:5]:
            lines.append(f"    • {pair}: {count} commits")

    # Time zone distribution
    tz = team_data['timezone_distribution']
    lines.append(f"\n  🌍 Time Zone Distribution")
    lines.append(f"  {'─'*45}")
    if tz.get('hours'):
        lines.append(f"  Commit hour distribution:")
        for hour, count in sorted(tz['hours'].items(), key=lambda x: -x[1])[:10]:
            h = int(hour)
            label = f"{h:02d}:00"
            bar_len = int(count / max(max(tz['hours'].values()), 1) * 30)
            bar = '█' * bar_len
            lines.append(f"    {label:<8s} {count:>5d} commits  {bar}")

    if tz.get('weekdays'):
        lines.append(f"\n  Weekday distribution:")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in day_order:
            count = tz['weekdays'].get(day, 0)
            if count > 0:
                short = day[:3]
                bar_len = int(count / max(max(tz['weekdays'].values()), 1) * 20)
                bar = '█' * bar_len
                lines.append(f"    {short:<5s} {count:>5d}  {bar}")

    # Onboarding complexity
    ob = team_data['onboarding']
    lines.append(f"\n  🎓 New Contributor Onboarding")
    lines.append(f"  {'─'*45}")
    lines.append(f"  Key files to understand:  {ob['key_file_count']}")
    lines.append(f"  Estimated files needed:  {ob['estimated_files']}")
    lines.append(f"  Onboarding complexity:    {ob['complexity_score']}/100")
    if ob['key_files']:
        lines.append(f"  Top files a new dev must know:")
        for f in ob['key_files'][:8]:
            authors_str = f" ({len(f['authors'])} authors)" if f.get('authors') else ""
            lines.append(f"    • {f['file']}{authors_str}")

    # Active/Inactive
    if team_data['inactive_developers']:
        lines.append(f"\n  💤 Inactive Contributors (no commits in 90 days)")
        for d in team_data['inactive_developers'][:10]:
            lines.append(f"    • {d['name']} ({d['commits']} total commits)")

    return '\n'.join(lines) + '\n'


# ── Internal functions ────────────────────────────────────────────────────

def _get_author_loc(path: str, authors: list) -> list:
    """Get lines added/removed per author from git log."""
    output = git_command(path, 'log', '--numstat', '--format=%aN', '-10000')
    if not output:
        return []

    author_stats = defaultdict(lambda: {'added': 0, 'removed': 0, 'commits': 0})
    current_author = None

    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) == 3:
            # numstat line
            added = int(parts[0]) if parts[0] != '-' else 0
            removed = int(parts[1]) if parts[1] != '-' else 0
            if current_author:
                author_stats[current_author]['added'] += added
                author_stats[current_author]['removed'] += removed
        else:
            # Author line
            current_author = line

    result = []
    author_commits = {a['name']: a['commits'] for a in authors}
    for name, stats in sorted(author_stats.items(), key=lambda x: x[1]['added'], reverse=True):
        result.append({
            'name': name,
            'added': stats['added'],
            'removed': stats['removed'],
            'net': stats['added'] - stats['removed'],
            'commits': author_commits.get(name, 0),
        })

    return result


def _get_author_files(path: str, authors: list) -> list:
    """Get count of unique files touched per author."""
    output = git_command(path, 'log', '--name-only', '--format=%aN', '-10000')
    if not output:
        return []

    author_files = defaultdict(set)
    current_author = None

    for line in output.split('\n'):
        line = line.strip()
        if line and not line.startswith('.') and '/' in line:
            if current_author:
                author_files[current_author].add(line)
        elif line:
            current_author = line

    result = []
    for name, files in sorted(author_files.items(), key=lambda x: len(x[1]), reverse=True):
        result.append({
            'name': name,
            'files': len(files),
            'top_files': sorted(files)[:5],
        })

    return result


def _get_author_commit_frequency(path: str) -> list:
    """Calculate commit frequency per author (commits per day)."""
    output = git_command(path, 'log', '--format=%aN|%aI', '-50000')
    if not output:
        return []

    author_dates = defaultdict(list)
    for line in output.split('\n'):
        if '|' not in line:
            continue
        name, date_str = line.split('|', 1)
        if name and date_str:
            try:
                dt = datetime.fromisoformat(date_str.strip())
                author_dates[name.strip()].append(dt)
            except ValueError:
                continue

    result = []
    for name, dates in sorted(author_dates.items(), key=lambda x: len(x[1]), reverse=True):
        if len(dates) < 2:
            result.append({
                'name': name,
                'commits': len(dates),
                'commits_per_day': 0.0,
                'first_commit': dates[0].isoformat() if dates else '',
                'last_commit': dates[-1].isoformat() if dates else '',
                'active_days': 1 if dates else 0,
            })
            continue

        date_range = (max(dates) - min(dates)).days
        active_days = len(set(d.date() for d in dates))
        commits_per_day = len(dates) / max(date_range, 1)

        result.append({
            'name': name,
            'commits': len(dates),
            'commits_per_day': round(commits_per_day, 3),
            'first_commit': min(dates).isoformat(),
            'last_commit': max(dates).isoformat(),
            'active_days': active_days,
        })

    return result


def _calculate_bus_factor_detailed(authors: list, total_commits: int) -> dict:
    """Calculate detailed bus factor analysis."""
    if not authors:
        return {'factor': 0, 'key_authors': [], 'coverage_by_count': []}

    cumulative = 0
    key_authors = []
    coverage_by_count = []

    for a in authors:
        cumulative += a['commits']
        pct = (cumulative / total_commits * 100) if total_commits > 0 else 0
        key_authors.append(a['name'])
        coverage_by_count.append({
            'people': len(key_authors),
            'coverage_pct': round(pct, 1),
        })
        if pct >= 50:
            break

    # Also calculate for 75% and 90%
    cumulative_75 = 0
    people_75 = 0
    cumulative_90 = 0
    people_90 = 0
    for a in authors:
        cumulative_75 += a['commits']
        people_75 += 1
        if cumulative_75 / total_commits >= 0.75:
            break

    for a in authors:
        cumulative_90 += a['commits']
        people_90 += 1
        if cumulative_90 / total_commits >= 0.90:
            break

    return {
        'factor': len(key_authors),
        'key_authors': key_authors,
        'coverage_by_count': coverage_by_count,
        'people_for_75pct': people_75,
        'people_for_90pct': people_90,
    }


def _compute_ownership(authors: list, total_commits: int) -> list:
    """Compute code ownership distribution as pie chart data."""
    if not authors or total_commits == 0:
        return []

    result = []
    other_commits = 0
    for i, a in enumerate(authors):
        pct = a['commits'] / total_commits * 100
        if i < 8:
            result.append({
                'name': a['name'],
                'commits': a['commits'],
                'percentage': round(pct, 1),
            })
        else:
            other_commits += a['commits']

    if other_commits > 0:
        result.append({
            'name': 'Others',
            'commits': other_commits,
            'percentage': round(other_commits / total_commits * 100, 1),
        })

    return result


def _estimate_review_coverage(path: str) -> dict:
    """Estimate review coverage from commit messages."""
    output = git_command(path, 'log', '--format=%b', '-5000')
    if not output:
        return {'reviewed': 0, 'total': 0, 'coverage_pct': 0.0}

    review_keywords = [
        r'\breview(ed|s|ing)?\b', r'\bapprove(d|s)?\b',
        r'\blgtm\b', r'\bship\s+it\b', r'\blooks\s+good\b',
        r'\br[+-]\b', r'\btested\b', r'\bverified\b',
    ]

    blocks = output.split('\n\n')
    reviewed = 0
    total = len(blocks)

    for block in blocks:
        block_lower = block.lower()
        for pattern in review_keywords:
            if re.search(pattern, block_lower):
                reviewed += 1
                break

    return {
        'reviewed': reviewed,
        'total': total,
        'coverage_pct': round(reviewed / max(total, 1) * 100, 1),
    }


def _detect_pair_programming(path: str) -> dict:
    """Detect pair programming from co-authored commits."""
    output = git_command(path, 'log', '--format=%b', '-10000')
    if not output:
        return {'coauthored_count': 0, 'pairs': []}

    coauthor_pattern = r'Co-authored-by:\s*(.+?)(?:<|$)'
    pairs = Counter()

    commits = output.split('\n\n')
    coauthored_count = 0

    for commit_body in commits:
        coauthors = re.findall(coauthor_pattern, commit_body, re.IGNORECASE)
        if len(coauthors) >= 2:
            coauthored_count += 1
            # Create pairs
            clean_authors = sorted(set(a.strip() for a in coauthors if a.strip()))
            for i in range(len(clean_authors)):
                for j in range(i + 1, len(clean_authors)):
                    pair_key = f"{clean_authors[i]} & {clean_authors[j]}"
                    pairs[pair_key] += 1
        elif len(coauthors) == 1:
            # Co-authored with main author
            coauthored_count += 1

    return {
        'coauthored_count': coauthored_count,
        'pairs': pairs.most_common(20),
    }


def _analyze_timezone_distribution(path: str) -> dict:
    """Analyze the time distribution of commits (hour, weekday)."""
    hours = get_contribution_by_hour(path, weeks=52)
    weekdays = get_contribution_by_weekday(path, weeks=52)

    # Determine work pattern
    peak_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else '00'
    peak_weekday = max(weekdays.items(), key=lambda x: x[1])[0] if weekdays else 'Monday'

    # Weekend ratio
    weekend_commits = sum(weekdays.get(d, 0) for d in ('Saturday', 'Sunday'))
    total_commits = sum(weekdays.values()) if weekdays else 1
    weekend_ratio = weekend_commits / total_commits

    # After-hours ratio (before 9am or after 6pm)
    after_hours = sum(hours.get(f'{h:02d}', 0) for h in range(24)
                      if h < 9 or h >= 18)
    total_hourly = sum(hours.values()) if hours else 1
    after_hours_ratio = after_hours / total_hourly

    return {
        'hours': hours,
        'weekdays': weekdays,
        'peak_hour': peak_hour,
        'peak_weekday': peak_weekday,
        'weekend_ratio': round(weekend_ratio, 3),
        'after_hours_ratio': round(after_hours_ratio, 3),
    }


def _compute_onboarding_complexity(path: str, author_files: list) -> dict:
    """Estimate how complex it is for a new contributor to onboard."""
    # Get files with most unique authors (knowledge spread)
    coauthored = get_file_coauthorship(path, limit=2000)

    # Files touched by many authors = shared knowledge
    # Files touched by few = knowledge silos
    if not coauthored:
        return {
            'key_file_count': 0,
            'estimated_files': 20,
            'complexity_score': 50,
            'key_files': [],
        }

    # Sort by author count (more authors = more important to understand)
    key_files = sorted(coauthored, key=lambda x: x['author_count'], reverse=True)[:20]

    # Count how many files a new dev would need to understand
    total_files = len(set(a['file'] for a in coauthored))
    # Assume they need to understand top 20% of most-touched files
    essential_files = max(int(total_files * 0.2), 10)

    # Complexity score based on:
    # - Number of key files (more = harder)
    # - Average author count (more authors = more context needed)
    # - File diversity
    avg_authors = sum(f['author_count'] for f in key_files) / max(len(key_files), 1)
    complexity = min(int(essential_files * 0.5 + avg_authors * 10), 100)

    return {
        'key_file_count': len(key_files),
        'estimated_files': essential_files,
        'complexity_score': complexity,
        'key_files': key_files,
    }


def _get_author_commit_sizes(path: str, authors: list) -> list:
    """Get average commit size per author."""
    output = git_command(path, 'log', '--shortstat', '--format=%aN', '-5000')
    if not output:
        return []

    author_changes = defaultdict(list)
    current_author = None

    for block in output.split('\n\n'):
        lines = block.strip().split('\n')
        if not lines:
            continue
        current_author = lines[0].strip()
        if not current_author:
            continue

        total_change = 0
        for line in lines[1:]:
            m = re.search(r'(\d+) insertion', line)
            if m:
                total_change += int(m.group(1))
            m = re.search(r'(\d+) deletion', line)
            if m:
                total_change += int(m.group(1))
        if total_change > 0:
            author_changes[current_author].append(total_change)

    result = []
    for name, changes in sorted(author_changes.items(), key=lambda x: len(x[1]), reverse=True):
        if changes:
            avg = sum(changes) / len(changes)
            median = sorted(changes)[len(changes) // 2]
            result.append({
                'name': name,
                'avg_commit_size': round(avg, 1),
                'median_commit_size': median,
                'max_commit_size': max(changes),
                'total_commits': len(changes),
            })

    return result


def _analyze_work_patterns(path: str) -> dict:
    """Analyze work patterns (hours, burst vs steady, streaks)."""
    output = git_command(path, 'log', '--format=%aI', '-50000')
    if not output:
        return {}

    dates = []
    for d in output.split('\n'):
        if not d.strip():
            continue
        try:
            dates.append(datetime.fromisoformat(d.strip()))
        except ValueError:
            continue

    if not dates:
        return {}

    # Commit bursts (multiple commits in short time)
    if len(dates) >= 2:
        gaps = []
        for i in range(1, min(len(dates), 1000)):
            gap = (dates[i] - dates[i-1]).total_seconds()
            if gap >= 0:
                gaps.append(gap)

        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            short_gaps = sum(1 for g in gaps if g < 60)  # Less than 1 minute
            burst_ratio = short_gaps / len(gaps)
        else:
            avg_gap = 0
            burst_ratio = 0
    else:
        avg_gap = 0
        burst_ratio = 0

    # Longest streak
    unique_dates = sorted(set(d.date() for d in dates))
    max_streak = 1
    current_streak = 1
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return {
        'avg_gap_seconds': round(avg_gap, 1),
        'burst_ratio': round(burst_ratio, 3),
        'max_consecutive_days': max_streak,
        'commit_style': 'bursty' if burst_ratio > 0.3 else 'steady' if burst_ratio < 0.1 else 'mixed',
    }


def _analyze_collaboration(path: str, authors: list,
                           author_files: list) -> dict:
    """Analyze collaboration patterns between developers."""
    if len(authors) < 2:
        return {
            'cross_author_files': 0,
            'collaboration_pairs': [],
            'silos': [],
        }

    # Get file→authors mapping
    output = git_command(path, 'log', '--name-only', '--format=%aN', '-5000')
    if not output:
        return {'cross_author_files': 0, 'collaboration_pairs': [], 'silos': []}

    file_authors = defaultdict(set)
    current_author = None

    for line in output.split('\n'):
        line = line.strip()
        if line and '/' in line and not line.startswith('.'):
            if current_author:
                file_authors[line].add(current_author)
        elif line:
            current_author = line

    # Cross-author files (files worked on by multiple people)
    cross_files = {f: authors for f, authors in file_authors.items() if len(authors) >= 2}
    solo_files = {f: next(iter(authors)) for f, authors in file_authors.items() if len(authors) == 1}

    # Find silos (authors who mostly work on their own files)
    author_solo = Counter()
    for f, author in solo_files.items():
        author_solo[author] += 1

    silos = []
    for a in authors:
        name = a['name']
        solo_count = author_solo.get(name, 0)
        total_files = sum(1 for af in author_files if af['name'] == name)
        if total_files > 0 and solo_count / total_files > 0.8 and total_files >= 3:
            silos.append({
                'name': name,
                'solo_files': solo_count,
                'total_files': total_files,
                'silo_ratio': round(solo_count / total_files, 2),
            })

    # Top collaboration pairs
    pair_counter = Counter()
    for f, auths in cross_files.items():
        auths_list = sorted(auths)
        for i in range(len(auths_list)):
            for j in range(i + 1, len(auths_list)):
                pair_counter[(auths_list[i], auths_list[j])] += 1

    collab_pairs = [
        {'pair': f"{a} & {b}", 'shared_files': count}
        for (a, b), count in pair_counter.most_common(15)
    ]

    return {
        'cross_author_files': len(cross_files),
        'total_shared_files': len(file_authors),
        'collaboration_pairs': collab_pairs,
        'silos': sorted(silos, key=lambda x: x['silo_ratio'], reverse=True)[:10],
    }


def _get_author_message_quality(path: str, authors: list) -> list:
    """Analyze commit message quality per author."""
    output = git_command(path, 'log', '--format=%aN|%s', '-5000')
    if not output:
        return []

    author_messages = defaultdict(list)
    for line in output.split('\n'):
        if '|' not in line:
            continue
        name, msg = line.split('|', 1)
        if name.strip() and msg.strip():
            author_messages[name.strip()].append(msg.strip())

    result = []
    conv_pattern = re.compile(
        r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?:\s+'
    )
    issue_pattern = re.compile(r'#\d+|[A-Z]+-\d+')

    for name, messages in sorted(author_messages.items(), key=lambda x: len(x[1]), reverse=True):
        if not messages:
            continue
        total = len(messages)
        lengths = [len(m) for m in messages]
        conventional = sum(1 for m in messages if conv_pattern.match(m))
        with_issue = sum(1 for m in messages if issue_pattern.search(m))
        avg_length = sum(lengths) / len(lengths)

        result.append({
            'name': name,
            'total_commits': total,
            'avg_message_length': round(avg_length, 1),
            'conventional_pct': round(conventional / total * 100, 1),
            'with_issue_ref_pct': round(with_issue / total * 100, 1),
            'quality_score': min(int(
                (conventional / total * 50) +
                (with_issue / total * 30) +
                (min(avg_length / 50, 1) * 20)
            ), 100),
        })

    return result

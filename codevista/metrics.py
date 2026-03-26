"""Metrics calculation and health scoring."""

from .security import security_score, security_summary


def calculate_health(analysis):
    """Calculate overall and per-category health scores."""
    scores = {}
    
    # Readability: based on comment ratio and average complexity
    total = analysis['total_lines']
    if total['total'] > 0:
        comment_ratio = total['comment'] / total['total']
    else:
        comment_ratio = 0
    scores['readability'] = min(100, int(comment_ratio * 300 + 50))  # 50-100 range
    if analysis['avg_complexity'] > 15:
        scores['readability'] = max(0, scores['readability'] - 30)
    elif analysis['avg_complexity'] > 8:
        scores['readability'] = max(0, scores['readability'] - 15)
    
    # Complexity
    avg_cc = analysis['avg_complexity']
    if avg_cc <= 5:
        scores['complexity'] = 95
    elif avg_cc <= 10:
        scores['complexity'] = 80
    elif avg_cc <= 20:
        scores['complexity'] = 60
    elif avg_cc <= 40:
        scores['complexity'] = 35
    else:
        scores['complexity'] = 15
    
    # Duplication
    dup_count = len(analysis['duplicates'])
    file_count = max(analysis['total_files'], 1)
    dup_ratio = dup_count / file_count
    if dup_ratio < 0.01:
        scores['duplication'] = 95
    elif dup_ratio < 0.05:
        scores['duplication'] = 80
    elif dup_ratio < 0.1:
        scores['duplication'] = 60
    elif dup_ratio < 0.2:
        scores['duplication'] = 35
    else:
        scores['duplication'] = 15
    
    # Coverage (comment coverage)
    if total['total'] > 0:
        coverage_pct = (total['comment'] / total['total']) * 100
    else:
        coverage_pct = 0
    scores['coverage'] = min(100, int(coverage_pct * 2))
    
    # Security
    scores['security'] = security_score(analysis['security_issues'])
    
    # Dependencies
    dep_count = len(analysis['dependencies'])
    if dep_count == 0:
        scores['dependencies'] = 100
    elif dep_count <= 10:
        scores['dependencies'] = 90
    elif dep_count <= 30:
        scores['dependencies'] = 70
    elif dep_count <= 50:
        scores['dependencies'] = 50
    else:
        scores['dependencies'] = 30
    
    if analysis['circular_deps']:
        scores['dependencies'] = max(0, scores['dependencies'] - 20)
    
    # Overall: weighted average
    weights = {'readability': 0.2, 'complexity': 0.2, 'duplication': 0.15,
               'coverage': 0.15, 'security': 0.15, 'dependencies': 0.15}
    overall = sum(scores[k] * weights[k] for k in weights)
    scores['overall'] = int(overall)
    
    return scores


def get_trend(score):
    """Get trend indicator for a score."""
    if score >= 80:
        return 'good'
    elif score >= 50:
        return 'warning'
    else:
        return 'critical'


def generate_recommendations(analysis, scores):
    """Generate specific recommendations based on metrics."""
    recs = []
    
    if scores['readability'] < 60:
        recs.append({
            'icon': '📖', 'category': 'Readability',
            'message': f"Average complexity is {analysis['avg_complexity']:.1f}. Consider breaking down complex functions into smaller, focused units.",
            'impact': 'high',
        })
    
    if scores['coverage'] < 50:
        total = analysis['total_lines']
        pct = (total['comment'] / total['total'] * 100) if total['total'] > 0 else 0
        recs.append({
            'icon': '💬', 'category': 'Documentation',
            'message': f"Comment coverage is only {pct:.1f}%. Add docstrings and inline comments to improve maintainability.",
            'impact': 'medium',
        })
    
    if analysis['duplicates']:
        recs.append({
            'icon': '♻️', 'category': 'Duplication',
            'message': f"Found {len(analysis['duplicates'])} duplicated code blocks. Extract shared logic into reusable functions.",
            'impact': 'high',
        })
    
    if analysis['security_issues']:
        crit = sum(1 for i in analysis['security_issues'] if i['severity'] == 'critical')
        recs.append({
            'icon': '🔒', 'category': 'Security',
            'message': f"Found {len(analysis['security_issues'])} security issues ({crit} critical). Move secrets to environment variables.",
            'impact': 'critical',
        })
    
    if analysis['circular_deps']:
        recs.append({
            'icon': '🔄', 'category': 'Dependencies',
            'message': f"Detected {len(analysis['circular_deps'])} circular import chains. Refactor module structure to break cycles.",
            'impact': 'high',
        })
    
    if len(analysis['dependencies']) > 30:
        recs.append({
            'icon': '📦', 'category': 'Dependencies',
            'message': f"Project has {len(analysis['dependencies'])} dependencies. Audit for unused packages.",
            'impact': 'medium',
        })
    
    if analysis['max_complexity'] > 20:
        complex_files = [f for f in analysis['files'] if f['complexity'] > 20][:5]
        names = ', '.join(f['path'] for f in complex_files)
        recs.append({
            'icon': '⚠️', 'category': 'Complexity',
            'message': f"Highest complexity score: {analysis['max_complexity']}. Hot spots: {names}",
            'impact': 'high',
        })
    
    if not recs:
        recs.append({
            'icon': '✨', 'category': 'Overall',
            'message': "Codebase looks healthy! Keep up the good work.",
            'impact': 'low',
        })
    
    return recs

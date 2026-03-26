"""Security scanning — secret detection, dangerous patterns."""

import os
import re
from collections import Counter


SECRET_PATTERNS = [
    (r'(?i)(?:aws_access_key_id|aws_secret)\s*=\s*["\']?[A-Z0-9]{20}', 'AWS Key', 'critical'),
    (r'(?i)akia[0-9a-z]{16}', 'AWS Access Key', 'critical'),
    (r'(?i)api[_-]?key\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', 'API Key', 'critical'),
    (r'(?i)password\s*[=:]\s*["\'][^"\']{4,}', 'Hardcoded Password', 'critical'),
    (r'(?i)secret[_-]?key\s*[=:]\s*["\'][^"\']{8,}', 'Secret Key', 'critical'),
    (r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----', 'Private Key', 'critical'),
    (r'(?i)github[_-]?token\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{30,}', 'GitHub Token', 'critical'),
    (r'(?i)(?:stripe|sk)_[a-z]{1,2}_[a-zA-Z0-9]{24,}', 'Stripe Key', 'critical'),
    (r'(?i)ghp_[a-zA-Z0-9]{36}', 'GitHub PAT', 'critical'),
    (r'(?i)glpat-[a-zA-Z0-9\-]{20,}', 'GitLab Token', 'critical'),
    (r'(?i)heroku[a-z0-9\-_]{30,}', 'Heroku Key', 'high'),
    (r'(?i)firebase[_-]?api[_-]?key\s*[=:]\s*["\']?[^"\']+', 'Firebase Key', 'high'),
    (r'(?i)(?:token|auth|bearer)\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{20,}', 'Generic Token', 'high'),
    (r'\b(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', 'Hardcoded IP', 'low'),
    (r'(?i)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'Hardcoded Email', 'low'),
]

DANGEROUS_FUNCTIONS = [
    (r'\beval\s*\(', 'eval() — code injection risk', 'high'),
    (r'\bexec\s*\(', 'exec() — code injection risk', 'high'),
    (r'\bsubprocess\s*\([^)]*shell\s*=\s*True', 'subprocess shell=True — command injection', 'high'),
    (r'\bos\.system\s*\(', 'os.system() — command injection', 'high'),
    (r'\bpickle\.loads?\s*\(', 'pickle — arbitrary code execution', 'high'),
    (r'\byaml\.load\s*\(', 'yaml.load() without SafeLoader — code execution', 'medium'),
    (r'\bmarshal\.loads?\s*\(', 'marshal — arbitrary code execution', 'high'),
    (r'\b__import__\s*\(', '__import__() — dynamic import risk', 'medium'),
    (r'\bcompile\s*\(', 'compile() — code injection risk', 'medium'),
    (r'\binput\s*\(', 'input() — potential injection in Python 2', 'low'),
    (r'\bassert\s*\(', 'assert — disabled with -O flag', 'low'),
    (r'\bgetattr\s*\([^,]+,\s*["\'][^"\']+["\']\s*,', 'getattr with string attr', 'low'),
]


def scan_file(filepath, content):
    """Scan a file for security issues."""
    issues = []
    rel = os.path.basename(filepath)
    
    for pattern, name, severity in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append({
                'file': filepath, 'type': 'secret', 'name': name,
                'severity': severity, 'count': len(matches), 'line': _find_line(content, pattern),
            })
    
    for pattern, name, severity in DANGEROUS_FUNCTIONS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append({
                'file': filepath, 'type': 'dangerous', 'name': name,
                'severity': severity, 'count': len(matches), 'line': _find_line(content, pattern),
            })
    
    # Check .env files
    if rel == '.env' or rel.endswith('.env'):
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        if lines:
            issues.append({
                'file': filepath, 'type': 'secret', 'name': '.env file with content',
                'severity': 'high', 'count': len(lines), 'line': 1,
            })
    
    return issues


def _find_line(content, pattern):
    """Find first line number matching pattern."""
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line):
            return i
    return 0


def security_score(issues):
    """Calculate security score 0-100."""
    if not issues:
        return 100
    weights = {'critical': 20, 'high': 10, 'medium': 5, 'low': 2}
    penalty = sum(weights.get(i['severity'], 2) * i['count'] for i in issues)
    return max(0, 100 - penalty)


def security_summary(issues):
    """Group issues by severity."""
    by_severity = Counter(i['severity'] for i in issues)
    by_type = Counter(i['type'] for i in issues)
    return {
        'total': len(issues),
        'by_severity': dict(by_severity),
        'by_type': dict(by_type),
        'score': security_score(issues),
    }

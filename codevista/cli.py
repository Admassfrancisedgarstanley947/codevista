"""CodeVista CLI — main entry point."""

import argparse
import os
import sys
import time
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser


def main():
    parser = argparse.ArgumentParser(
        prog='codevista',
        description='🔍 CodeVista — Google Analytics for your code'
    )
    sub = parser.add_subparsers(dest='command')

    # analyze
    p = sub.add_parser('analyze', help='Full codebase analysis')
    p.add_argument('path', help='Project directory')
    p.add_argument('-o', '--output', default='report.html', help='Output HTML file')
    p.add_argument('--no-git', action='store_true', help='Skip git analysis')
    p.add_argument('--depth', type=int, default=None, help='Max directory depth')

    # quick
    p = sub.add_parser('quick', help='Fast analysis')
    p.add_argument('path', help='Project directory')
    p.add_argument('-o', '--output', default='report.html')

    # serve
    p = sub.add_parser('serve', help='Serve report on local server')
    p.add_argument('path', help='Project directory')
    p.add_argument('--port', type=int, default=8080)

    # compare
    p = sub.add_parser('compare', help='Compare two codebases')
    p.add_argument('path1', help='First project directory')
    p.add_argument('path2', help='Second project directory')
    p.add_argument('-o', '--output', default='comparison.html')

    # watch
    p = sub.add_parser('watch', help='Re-analyze on file changes')
    p.add_argument('path', help='Project directory')
    p.add_argument('-o', '--output', default='report.html')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'quick':
        cmd_quick(args)
    elif args.command == 'serve':
        cmd_serve(args)
    elif args.command == 'compare':
        cmd_compare(args)
    elif args.command == 'watch':
        cmd_watch(args)


def cmd_analyze(args):
    from .analyzer import analyze_project
    from .report import generate_report
    from .metrics import calculate_health

    path = args.path
    if not os.path.isdir(path):
        print(f"❌ Directory not found: {path}")
        sys.exit(1)

    print(f"🔍 Analyzing {os.path.abspath(path)}...")
    start = time.time()

    analysis = analyze_project(path, max_depth=args.depth, include_git=not args.no_git)
    scores = calculate_health(analysis)

    elapsed = time.time() - start
    report = generate_report(analysis, args.output)

    print(f"✅ Report generated: {args.output}")
    print(f"   📁 {analysis['total_files']} files analyzed")
    print(f"   📊 {analysis['total_lines']['code']:,} lines of code")
    print(f"   🧩 {len(analysis['languages'])} languages detected")
    print(f"   🏥 Health score: {scores['overall']}/100")
    print(f"   ⏱️  Analysis completed in {elapsed:.2f}s")


def cmd_quick(args):
    from .analyzer import analyze_project
    from .report import generate_report

    print(f"⚡ Quick analysis of {args.path}...")
    start = time.time()

    analysis = analyze_project(args.path, max_depth=3, include_git=False)
    report = generate_report(analysis, args.output)

    print(f"✅ Quick report: {args.output} ({time.time()-start:.2f}s)")


def cmd_serve(args):
    from .analyzer import analyze_project
    from .report import generate_report

    output = '.codevista-serve.html'
    print(f"🌐 Analyzing {args.path}...")
    analysis = analyze_project(args.path)
    generate_report(analysis, output)

    os.chdir(os.path.dirname(os.path.abspath(output)))
    handler = SimpleHTTPRequestHandler

    class Handler(handler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/' + output
            return super().do_GET()

    server = HTTPServer(('0.0.0.0', args.port), Handler)
    url = f'http://localhost:{args.port}'
    print(f"🚀 Serving report at {url}")
    print(f"   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.server_close()
        os.remove(output)


def cmd_compare(args):
    from .analyzer import analyze_project
    from .report import generate_report
    from .metrics import calculate_health

    print(f"📊 Comparing {args.path1} vs {args.path2}...")

    a1 = analyze_project(args.path1)
    a2 = analyze_project(args.path2)
    s1 = calculate_health(a1)
    s2 = calculate_health(a2)

    # Generate comparison summary
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CodeVista Comparison</title>
<style>
:root {{ --bg:#0f0e17; --surface:#1a1a2e; --text:#fffffe; --text2:#a7a9be; --primary:#7f5af0; --green:#2cb67d; --accent:#e53170; --warning:#ff8906; --radius:12px; }}
body {{ background:var(--bg); color:var(--text); font-family:-apple-system,sans-serif; margin:0; padding:24px; }}
.container {{ max-width:1000px; margin:0 auto; }}
h1 {{ text-align:center; font-size:2em; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:24px; }}
.card {{ background:var(--surface); border-radius:var(--radius); padding:24px; border:1px solid rgba(127,90,240,0.15); }}
.card h2 {{ font-size:1.3em; margin-bottom:12px; }}
.metric {{ display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05); }}
.metric .label {{ color:var(--text2); }}
.vs {{ display:flex; align-items:center; justify-content:center; font-size:1.5em; color:var(--text2); padding:16px; }}
</style></head><body>
<div class="container">
<h1>📊 CodeVista Comparison</h1>
<div class="grid">
  <div class="card"><h2>{_esc(os.path.basename(args.path1))}</h2>
    <div class="metric"><span class="label">Files</span><span>{a1["total_files"]}</span></div>
    <div class="metric"><span class="label">Lines of Code</span><span>{a1["total_lines"]["code"]:,}</span></div>
    <div class="metric"><span class="label">Languages</span><span>{len(a1["languages"])}</span></div>
    <div class="metric"><span class="label">Avg Complexity</span><span>{a1["avg_complexity"]:.1f}</span></div>
    <div class="metric"><span class="label">Security Issues</span><span>{len(a1["security_issues"])}</span></div>
    <div class="metric"><span class="label">Dependencies</span><span>{len(a1["dependencies"])}</span></div>
    <div class="metric"><span class="label" style="font-size:1.2em;font-weight:700">Health Score</span><span style="font-size:1.4em;color:{_score_color(s1["overall"])}">{s1["overall"]}</span></div>
  </div>
  <div class="card"><h2>{_esc(os.path.basename(args.path2))}</h2>
    <div class="metric"><span class="label">Files</span><span>{a2["total_files"]}</span></div>
    <div class="metric"><span class="label">Lines of Code</span><span>{a2["total_lines"]["code"]:,}</span></div>
    <div class="metric"><span class="label">Languages</span><span>{len(a2["languages"])}</span></div>
    <div class="metric"><span class="label">Avg Complexity</span><span>{a2["avg_complexity"]:.1f}</span></div>
    <div class="metric"><span class="label">Security Issues</span><span>{len(a2["security_issues"])}</span></div>
    <div class="metric"><span class="label">Dependencies</span><span>{len(a2["dependencies"])}</span></div>
    <div class="metric"><span class="label" style="font-size:1.2em;font-weight:700">Health Score</span><span style="font-size:1.4em;color:{_score_color(s2["overall"])}">{s2["overall"]}</span></div>
  </div>
</div>
<div class="vs">VS</div>
</div></body></html>'''

    with open(args.output, 'w') as f:
        f.write(html)
    print(f"✅ Comparison saved: {args.output}")


def cmd_watch(args):
    from .analyzer import analyze_project
    from .report import generate_report

    path = os.path.abspath(args.path)
    print(f"👁️  Watching {path} for changes...")

    last_mtime = _get_max_mtime(path)
    while True:
        try:
            import time
            time.sleep(3)
            current = _get_max_mtime(path)
            if current > last_mtime:
                last_mtime = current
                print(f"🔄 Change detected, re-analyzing...")
                analysis = analyze_project(path)
                generate_report(analysis, args.output)
                print(f"✅ Report updated: {args.output}")
        except KeyboardInterrupt:
            print("\n👋 Watch stopped")
            break


def _get_max_mtime(path):
    """Get the latest modification time in a directory tree."""
    latest = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for f in files:
            try:
                mtime = os.path.getmtime(os.path.join(root, f))
                if mtime > latest:
                    latest = mtime
            except OSError:
                continue
    return latest


def _esc(s):
    import html
    return html.escape(str(s))

def _score_color(score):
    if score >= 80: return '#2cb67d'
    if score >= 50: return '#ff8906'
    return '#e53170'


if __name__ == '__main__':
    main()

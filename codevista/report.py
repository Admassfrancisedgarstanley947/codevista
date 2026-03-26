"""HTML report generator — self-contained, beautiful, interactive."""

import json
import os
import html
from datetime import datetime

from .metrics import calculate_health, get_trend, generate_recommendations
from .security import security_summary
from .languages import get_lang_color


def generate_report(analysis, output_path=None):
    """Generate a self-contained HTML report."""
    scores = calculate_health(analysis)
    recommendations = generate_recommendations(analysis, scores)
    sec_sum = security_summary(analysis['security_issues'])
    
    report_html = build_html(analysis, scores, recommendations, sec_sum)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
    
    return report_html


def esc(s):
    return html.escape(str(s), quote=True)


def score_color(score):
    if score >= 80:
        return '#2cb67d'
    elif score >= 50:
        return '#ff8906'
    return '#e53170'


def trend_icon(trend):
    return {'good': '✅', 'warning': '⚠️', 'critical': '❌'}.get(trend, '❓')


def build_html(analysis, scores, recommendations, sec_sum):
    """Build the complete HTML report."""
    a = analysis
    tl = a['total_lines']
    lang_json = json.dumps(a['languages'])
    files_json = json.dumps([{
        'path': f['path'], 'lang': f['language'], 'color': f['color'],
        'total': f['lines']['total'], 'code': f['lines']['code'],
        'comment': f['lines']['comment'], 'blank': f['lines']['blank'],
        'complexity': f['complexity'], 'size': f['size'],
    } for f in a['files']])
    
    # Top files by lines
    top_files = sorted(a['files'], key=lambda x: x['lines']['total'], reverse=True)[:15]
    
    # Language pie chart SVG
    lang_total = sum(a['languages'].values()) or 1
    pie_svg = build_pie_svg(a['languages'], lang_total)
    
    # Bar chart SVG
    bar_svg = build_bar_svg(top_files)
    
    # Complexity chart
    comp_files = sorted(a['files'], key=lambda x: x['complexity'], reverse=True)[:10]
    comp_svg = build_complexity_svg(comp_files)
    
    # File size distribution
    size_dist = build_size_distribution(a['files'])
    size_svg = build_size_dist_svg(size_dist)
    
    # Git heatmap
    heatmap_svg = ''
    if a['git'] and a['git']['heatmap']:
        heatmap_svg = build_heatmap_svg(a['git']['heatmap'])
    
    # Security issues HTML
    sec_html = build_security_html(a['security_issues'])
    
    # Recommendations HTML
    recs_html = build_recommendations_html(recommendations)
    
    # Dependencies HTML
    deps_html = build_deps_html(a)
    
    # Dir tree HTML
    tree_html = build_tree_html(a['dir_tree'])
    
    # Git stats HTML
    git_html = build_git_html(a['git'])
    
    # Tech badges
    badges = ''.join(
        f'<span class="badge">{esc(fw)}</span>' for fw in a['frameworks']
    )
    lang_badges = ''.join(
        f'<span class="badge lang-badge" style="border-color:{get_lang_color(l)}; color:{get_lang_color(l)}">{esc(l)} ({a["languages"][l]})</span>'
        for l in sorted(a['languages'].keys(), key=lambda x: a['languages'][x], reverse=True)[:15]
    )
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeVista — {esc(a["project_name"])}</title>
<style>
:root {{
  --bg: #0f0e17; --surface: #1a1a2e; --surface2: #232340;
  --text: #fffffe; --text2: #a7a9be;
  --primary: #7f5af0; --primary2: #2cb67d; --accent: #e53170; --warning: #ff8906;
  --radius: 12px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6; min-height: 100vh;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
header {{
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  border-radius: var(--radius); padding: 40px; margin-bottom: 24px;
  position: relative; overflow: hidden;
}}
header::before {{
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
}}
header h1 {{ font-size: 2.2em; font-weight: 800; position: relative; }}
header .subtitle {{ opacity: 0.85; margin-top: 4px; font-size: 1.1em; position: relative; }}
header .meta {{ margin-top: 16px; opacity: 0.7; font-size: 0.9em; position: relative; }}

/* Health Score */
.health-ring {{
  width: 120px; height: 120px; position: absolute; right: 40px; top: 50%; transform: translateY(-50%);
}}
.health-ring svg {{ width: 120px; height: 120px; }}
.health-ring .score-text {{
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 2em; font-weight: 800;
}}

/* Stats grid */
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.stat-card {{
  background: var(--surface); border-radius: var(--radius); padding: 20px;
  border: 1px solid rgba(127,90,240,0.15); transition: transform 0.2s, box-shadow 0.2s;
}}
.stat-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(127,90,240,0.15); }}
.stat-card .label {{ color: var(--text2); font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
.stat-card .value {{ font-size: 2em; font-weight: 700; margin-top: 4px; }}
.stat-card .sub {{ color: var(--text2); font-size: 0.85em; margin-top: 4px; }}

/* Score cards */
.scores-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 24px; }}
.score-card {{
  background: var(--surface); border-radius: var(--radius); padding: 16px; text-align: center;
  border: 1px solid rgba(127,90,240,0.1);
}}
.score-card .score-label {{ color: var(--text2); font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px; }}
.score-card .score-value {{ font-size: 1.8em; font-weight: 700; margin: 4px 0; }}
.score-card .trend {{ font-size: 1.2em; }}

/* Sections */
.section {{
  background: var(--surface); border-radius: var(--radius); padding: 24px;
  margin-bottom: 24px; border: 1px solid rgba(127,90,240,0.1);
}}
.section h2 {{
  font-size: 1.3em; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}}
.section h2 .icon {{ font-size: 1.4em; }}
.section.collapsed .section-body {{ display: none; }}
.section-header {{
  cursor: pointer; user-select: none; display: flex; align-items: center;
  justify-content: space-between;
}}
.section-header .toggle {{ color: var(--text2); font-size: 1.2em; transition: transform 0.2s; }}
.section.collapsed .toggle {{ transform: rotate(-90deg); }}

/* Badges */
.badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
.badge {{
  background: rgba(127,90,240,0.15); color: var(--primary); padding: 4px 12px;
  border-radius: 20px; font-size: 0.85em; font-weight: 500;
  border: 1px solid rgba(127,90,240,0.3);
}}
.lang-badge {{ background: transparent; }}

/* Table */
.table-wrap {{ overflow-x: auto; margin-top: 12px; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{
  text-align: left; padding: 10px 12px; color: var(--text2); font-size: 0.8em;
  text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid rgba(127,90,240,0.2);
  cursor: pointer; user-select: none;
}}
th:hover {{ color: var(--primary); }}
td {{ padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.9em; }}
tr:hover {{ background: rgba(127,90,240,0.05); }}

/* Security */
.sec-item {{
  display: flex; align-items: flex-start; gap: 12px; padding: 12px;
  background: var(--surface2); border-radius: 8px; margin-bottom: 8px;
  border-left: 3px solid var(--accent);
}}
.sec-item.high {{ border-left-color: var(--warning); }}
.sec-item.critical {{ border-left-color: var(--accent); }}
.sec-item.medium {{ border-left-color: var(--primary); }}
.sec-item.low {{ border-left-color: var(--text2); }}
.severity-badge {{
  padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: 600;
  text-transform: uppercase;
}}
.severity-badge.critical {{ background: rgba(229,49,112,0.2); color: var(--accent); }}
.severity-badge.high {{ background: rgba(255,137,6,0.2); color: var(--warning); }}
.severity-badge.medium {{ background: rgba(127,90,240,0.2); color: var(--primary); }}
.severity-badge.low {{ background: rgba(167,169,190,0.2); color: var(--text2); }}

/* Recommendations */
.rec {{
  display: flex; gap: 12px; padding: 12px; background: var(--surface2);
  border-radius: 8px; margin-bottom: 8px;
}}
.rec .icon {{ font-size: 1.5em; flex-shrink: 0; }}
.rec .content {{ flex: 1; }}
.rec .category {{ font-size: 0.8em; color: var(--primary); font-weight: 600; text-transform: uppercase; }}

/* Directory tree */
.tree {{ font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.85em; line-height: 1.8; }}
.tree .dir {{ color: var(--primary); font-weight: 600; }}
.tree .file {{ color: var(--text2); }}
.tree .size {{ color: var(--text2); opacity: 0.5; }}

/* Search */
.search {{
  width: 100%; padding: 10px 16px; background: var(--surface2);
  border: 1px solid rgba(127,90,240,0.2); border-radius: 8px;
  color: var(--text); font-size: 0.95em; margin-bottom: 16px; outline: none;
}}
.search:focus {{ border-color: var(--primary); }}
.search::placeholder {{ color: var(--text2); }}

/* Filter pills */
.filters {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
.filter-pill {{
  padding: 4px 12px; border-radius: 16px; font-size: 0.8em; cursor: pointer;
  background: var(--surface2); color: var(--text2); border: 1px solid transparent;
  transition: all 0.2s;
}}
.filter-pill:hover, .filter-pill.active {{ background: rgba(127,90,240,0.2); color: var(--primary); border-color: var(--primary); }}

/* SVG charts */
.chart-container {{ margin: 16px 0; overflow-x: auto; }}
.chart-container svg {{ display: block; }}

/* Dark/light toggle */
.theme-toggle {{
  position: fixed; bottom: 24px; right: 24px; width: 48px; height: 48px;
  border-radius: 50%; background: var(--surface); border: 1px solid rgba(127,90,240,0.3);
  color: var(--text); font-size: 1.4em; cursor: pointer; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}
.theme-toggle:hover {{ transform: scale(1.1); }}

/* Print */
@media print {{
  body {{ background: white; color: black; }}
  .theme-toggle {{ display: none; }}
  header {{ background: #7f5af0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .section {{ break-inside: avoid; border: 1px solid #ddd; background: white; }}
}}

/* Responsive */
@media (max-width: 768px) {{
  header {{ padding: 24px; }}
  .health-ring {{ width: 80px; height: 80px; right: 20px; }}
  .stats {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🔍 CodeVista</h1>
    <div class="subtitle">{esc(a["project_name"])} — Codebase Analysis Report</div>
    <div class="meta">Generated {now} • {a["total_files"]} files • {tl["total"]:,} lines of code</div>
    <div class="health-ring">
      <svg viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="8"/>
        <circle cx="60" cy="60" r="52" fill="none" stroke="{score_color(scores["overall"])}" stroke-width="8"
          stroke-dasharray="{scores["overall"] * 3.267} 326.7" stroke-linecap="round"
          transform="rotate(-90 60 60)" style="transition: stroke-dasharray 1s ease;"/>
      </svg>
      <div class="score-text" style="color:{score_color(scores["overall"])}">{scores["overall"]}</div>
    </div>
  </header>

  <div class="stats">
    <div class="stat-card">
      <div class="label">Files</div>
      <div class="value">{a["total_files"]}</div>
      <div class="sub">source files analyzed</div>
    </div>
    <div class="stat-card">
      <div class="label">Lines of Code</div>
      <div class="value">{tl["code"]:,}</div>
      <div class="sub">{tl["comment"]:,} comments • {tl["blank"]:,} blank</div>
    </div>
    <div class="stat-card">
      <div class="label">Languages</div>
      <div class="value">{len(a["languages"])}</div>
      <div class="sub">{", ".join(sorted(a["languages"].keys(), key=lambda x: a["languages"][x], reverse=True)[:5])}</div>
    </div>
    <div class="stat-card">
      <div class="label">Complexity</div>
      <div class="value">{a["avg_complexity"]:.1f}</div>
      <div class="sub">avg cyclomatic (max {a["max_complexity"]})</div>
    </div>
    <div class="stat-card">
      <div class="label">Security Issues</div>
      <div class="value">{sec_sum["total"]}</div>
      <div class="sub">{"critical" if sec_sum["by_severity"].get("critical") else "score: " + str(sec_sum["score"])}</div>
    </div>
    <div class="stat-card">
      <div class="label">Dependencies</div>
      <div class="value">{len(a["dependencies"])}</div>
      <div class="sub">{esc(a["package_manager"] or "none detected")}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">📊</span> Health Scores</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">
      <div class="scores-grid">
        {" ".join(f'''
        <div class="score-card">
          <div class="score-label">{cat.replace("_", " ").title()}</div>
          <div class="score-value" style="color:{score_color(scores[cat])}">{scores[cat]}</div>
          <div class="trend">{trend_icon(get_trend(scores[cat]))}</div>
        </div>''' for cat in ['readability', 'complexity', 'duplication', 'coverage', 'security', 'dependencies'])}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">🧩</span> Technology Stack</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">
      <div style="margin-bottom:12px"><strong>Languages:</strong></div>
      <div class="badges">{lang_badges}</div>
      {f'<div style="margin-top:16px;margin-bottom:12px"><strong>Frameworks:</strong></div><div class="badges">{badges}</div>' if a["frameworks"] else ''}
      <div class="chart-container">{pie_svg}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">📁</span> Project Structure</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">
      <div class="tree">{tree_html}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">📈</span> Code Metrics</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">
      <h3 style="margin-bottom:8px">Top Files by Lines of Code</h3>
      <div class="chart-container">{bar_svg}</div>
      <h3 style="margin:16px 0 8px">Complexity Hot Spots</h3>
      <div class="chart-container">{comp_svg}</div>
      <h3 style="margin:16px 0 8px">File Size Distribution</h3>
      <div class="chart-container">{size_svg}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">📋</span> All Files</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">
      <input type="text" class="search" placeholder="Search files..." id="fileSearch" oninput="filterFiles()">
      <div class="filters" id="langFilters"></div>
      <div class="table-wrap">
        <table id="filesTable">
          <thead>
            <tr>
              <th onclick="sortTable(0)">File</th>
              <th onclick="sortTable(1)">Language</th>
              <th onclick="sortTable(2)">Lines</th>
              <th onclick="sortTable(3)">Code</th>
              <th onclick="sortTable(4)">Comments</th>
              <th onclick="sortTable(5)">Complexity</th>
              <th onclick="sortTable(6)">Size</th>
            </tr>
          </thead>
          <tbody id="filesBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  {f'''<div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">🔒</span> Security Scan</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">{sec_html}</div>
  </div>''' if sec_sum["total"] > 0 else ''}

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">📦</span> Dependencies</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">{deps_html}</div>
  </div>

  {f'''<div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">👥</span> Git Insights</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">{git_html}<div class="chart-container">{heatmap_svg}</div></div>
  </div>''' if a['git'] else ''}

  <div class="section">
    <div class="section-header" onclick="toggleSection(this)">
      <h2><span class="icon">💡</span> Recommendations</h2>
      <span class="toggle">▼</span>
    </div>
    <div class="section-body">{recs_html}</div>
  </div>

</div>

<button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">🌙</button>

<script>
const FILES = {files_json};
const LANGS = {lang_json};
let currentLang = null;
let sortCol = 2, sortAsc = false;

// Init lang filters
const filtersEl = document.getElementById('langFilters');
Object.keys(LANGS).sort((a,b) => LANGS[b]-LANGS[a]).forEach(l => {{
  const pill = document.createElement('span');
  pill.className = 'filter-pill';
  pill.textContent = l;
  pill.onclick = () => {{
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    if (currentLang === l) {{ currentLang = null; }} else {{ currentLang = l; pill.classList.add('active'); }}
    renderFiles();
  }};
  filtersEl.appendChild(pill);
}});

function renderFiles() {{
  const q = (document.getElementById('fileSearch')?.value || '').toLowerCase();
  const rows = FILES.filter(f => {{
    if (currentLang && f.lang !== currentLang) return false;
    if (q && !f.path.toLowerCase().includes(q)) return false;
    return true;
  }}).sort((a, b) => {{
    const keys = ['path','lang','total','code','comment','complexity','size'];
    const va = a[keys[sortCol]], vb = b[keys[sortCol]];
    if (typeof va === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortAsc ? va - vb : vb - va;
  }});
  const body = document.getElementById('filesBody');
  body.innerHTML = rows.map(f => `<tr>
    <td style="font-family:monospace;font-size:0.85em">${{esc(f.path)}}</td>
    <td><span style="color:${{f.color}}">${{esc(f.lang)}}</span></td>
    <td>${{f.total}}</td><td>${{f.code}}</td><td>${{f.comment}}</td>
    <td style="color:${{f.complexity>15?'#e53170':f.complexity>8?'#ff8906':'#2cb67d'}}">${{f.complexity}}</td>
    <td>${{formatSize(f.size)}}</td>
  </tr>`).join('');
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}
function formatSize(b) {{ return b < 1024 ? b+'B' : b < 1048576 ? (b/1024).toFixed(1)+'KB' : (b/1048576).toFixed(1)+'MB'; }}
function filterFiles() {{ renderFiles(); }}
function sortTable(col) {{ if (sortCol === col) sortAsc = !sortAsc; else {{ sortCol = col; sortAsc = col === 0; }} renderFiles(); }}

function toggleSection(el) {{ el.parentElement.classList.toggle('collapsed'); }}

function toggleTheme() {{
  const light = {{
    '--bg':'#fffffe','--surface':'#f0f0f5','--surface2':'#e8e8f0',
    '--text':'#0f0e17','--text2':'#52525b',
  }};
  const dark = {{
    '--bg':'#0f0e17','--surface':'#1a1a2e','--surface2':'#232340',
    '--text':'#fffffe','--text2':'#a7a9be',
  }};
  const isLight = document.body.style.getPropertyValue('--bg') === light['--bg'];
  const theme = isLight ? dark : light;
  Object.entries(theme).forEach(([k,v]) => document.body.style.setProperty(k, v));
  document.querySelector('.theme-toggle').textContent = isLight ? '🌙' : '☀️';
}}

renderFiles();
</script>
</body>
</html>'''


def build_pie_svg(languages, total):
    if not languages:
        return '<div style="color:var(--text2)">No languages detected</div>'
    cx, cy, r = 100, 100, 80
    slices = []
    angle = 0
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        pct = count / total
        sweep = pct * 360
        color = get_lang_color(lang)
        x1 = cx + r * _cos(angle)
        y1 = cy + r * _sin(angle)
        x2 = cx + r * _cos(angle + sweep)
        y2 = cy + r * _sin(angle + sweep)
        large = 1 if sweep > 180 else 0
        slices.append(f'<path d="M{cx},{cy} L{x1},{y1} A{r},{r} 0 {large},1 {x2},{y2} Z" fill="{color}" opacity="0.85"/>')
        angle += sweep
    legend = ''.join(
        f'<rect x="220" y="{i*22}" width="12" height="12" rx="3" fill="{get_lang_color(l)}"/>'
        f'<text x="238" y="{i*22+10}" fill="var(--text2)" font-size="11">{esc(l)} ({c:,})</text>'
        for i, (l, c) in enumerate(sorted(languages.items(), key=lambda x: -x[1])[:12])
    )
    return f'<svg viewBox="0 0 500 300" width="500" height="300">{"".join(slices)}{legend}</svg>'


def build_bar_svg(top_files):
    if not top_files:
        return ''
    max_val = max(f['lines']['total'] for f in top_files) or 1
    bars = ''
    for i, f in enumerate(top_files):
        h = (f['lines']['total'] / max_val) * 280
        y = 300 - h
        name = f['path'].split('/')[-1][:20]
        bars += f'''<rect x="{i*52+10}" y="{y}" width="40" height="{h}" rx="4" fill="{f['color']}" opacity="0.8">
      <title>{esc(f['path'])}: {f['lines']['total']} lines</title></rect>
      <text x="{i*52+30}" y="{y-6}" fill="var(--text2)" font-size="9" text-anchor="middle">{f['lines']['total']}</text>
      <text x="{i*52+30}" y="316" fill="var(--text2)" font-size="8" text-anchor="middle" transform="rotate(-45 {i*52+30} 316)">{esc(name)}</text>'''
    return f'<svg viewBox="0 0 {len(top_files)*52+20} 360" width="100%" height="360">{bars}</svg>'


def build_complexity_svg(files):
    if not files:
        return ''
    max_val = max(f['complexity'] for f in files) or 1
    bars = ''
    for i, f in enumerate(files):
        h = (f['complexity'] / max_val) * 220
        y = 240 - h
        color = '#e53170' if f['complexity'] > 15 else '#ff8906' if f['complexity'] > 8 else '#2cb67d'
        name = f['path'].split('/')[-1][:18]
        bars += f'''<rect x="{i*58+10}" y="{y}" width="46" height="{h}" rx="4" fill="{color}" opacity="0.8">
      <title>{esc(f['path'])}: complexity {f['complexity']}</title></rect>
      <text x="{i*58+33}" y="{y-6}" fill="var(--text2)" font-size="10" text-anchor="middle">{f['complexity']}</text>
      <text x="{i*58+33}" y="256" fill="var(--text2)" font-size="8" text-anchor="middle" transform="rotate(-45 {i*58+33} 256)">{esc(name)}</text>'''
    return f'<svg viewBox="0 0 {len(files)*58+20} 290" width="100%" height="290">{bars}</svg>'


def build_size_distribution(files):
    bins = {'Tiny (<1KB)': 0, 'Small (1-10KB)': 0, 'Medium (10-50KB)': 0, 'Large (50-200KB)': 0, 'Huge (200KB+)': 0}
    for f in files:
        s = f['size']
        if s < 1024: bins['Tiny (<1KB)'] += 1
        elif s < 10240: bins['Small (1-10KB)'] += 1
        elif s < 51200: bins['Medium (10-50KB)'] += 1
        elif s < 204800: bins['Large (50-200KB)'] += 1
        else: bins['Huge (200KB+)'] += 1
    return bins


def build_size_dist_svg(dist):
    max_val = max(dist.values()) or 1
    bars = ''
    colors = ['#2cb67d', '#7f5af0', '#ff8906', '#e53170', '#e53170']
    for i, (label, count) in enumerate(dist.items()):
        h = (count / max_val) * 180
        y = 200 - h
        bars += f'''<rect x="{i*110+20}" y="{y}" width="90" height="{h}" rx="6" fill="{colors[i]}" opacity="0.8"/>
      <text x="{i*110+65}" y="{y-6}" fill="var(--text2)" font-size="11" text-anchor="middle">{count}</text>
      <text x="{i*110+65}" y="218" fill="var(--text2)" font-size="9" text-anchor="middle">{esc(label)}</text>'''
    return f'<svg viewBox="0 0 {len(dist)*110+40} 240" width="100%" height="240">{bars}</svg>'


def build_heatmap_svg(heatmap):
    from datetime import date, timedelta
    # Last 52 weeks
    weeks = 52
    days = 7
    cell_size = 12
    gap = 2
    max_count = max(heatmap.values()) if heatmap else 1
    rects = ''
    for w in range(weeks):
        for d in range(days):
            try:
                dt = date.today() - timedelta(days=(weeks - 1 - w) * 7 + (6 - d))
                ds = dt.isoformat()
                count = heatmap.get(ds, 0)
            except (ValueError, OverflowError):
                count = 0
            intensity = count / max_count if max_count > 0 else 0
            opacity = 0.1 + intensity * 0.9
            color = '#2cb67d' if count > 0 else 'rgba(255,255,255,0.05)'
            x = w * (cell_size + gap) + 40
            y = d * (cell_size + gap) + 30
            rects += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" opacity="{opacity:.2f}" title="{ds}: {count} commits"/>'
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_labels = ''.join(f'<text x="{i*(cell_size+gap)*4.3+40}" y="20" fill="var(--text2)" font-size="9">{m}</text>' for i, m in enumerate(months[:13]))
    day_labels = ''.join(f'<text x="0" y="{d*(cell_size+gap)+38}" fill="var(--text2)" font-size="8">{["Mon","","Wed","","Fri","",""][d]}</text>' for d in range(days))
    width = weeks * (cell_size + gap) + 60
    return f'<svg viewBox="0 0 {width} 140" width="100%" height="140">{month_labels}{day_labels}{rects}</svg>'


def build_security_html(issues):
    if not issues:
        return '<div style="color:var(--primary2)">✅ No security issues detected!</div>'
    items = []
    for issue in sorted(issues, key=lambda x: {'critical':0,'high':1,'medium':2,'low':3}.get(x['severity'], 4))[:30]:
        items.append(f'''<div class="sec-item {esc(issue['severity'])}">
      <div><span class="severity-badge {esc(issue['severity'])}">{esc(issue['severity'])}</span></div>
      <div>
        <div style="font-weight:600">{esc(issue['name'])}</div>
        <div style="font-size:0.85em;color:var(--text2)">{esc(issue['file'].split('/')[-1])} — line {issue['line']} • {issue['count']} occurrence(s)</div>
      </div>
    </div>''')
    return '\n'.join(items)


def build_recommendations_html(recs):
    items = []
    for r in recs:
        items.append(f'''<div class="rec">
      <div class="icon">{r['icon']}</div>
      <div class="content">
        <div class="category">{esc(r['category'])}</div>
        <div>{esc(r['message'])}</div>
      </div>
    </div>''')
    return '\n'.join(items)


def build_deps_html(analysis):
    deps = analysis['dependencies']
    if not deps:
        return f'<div style="color:var(--text2)">No dependencies detected (no {analysis["package_manager"] or "package"} file found)</div>'
    pm = analysis['package_manager'] or 'unknown'
    rows = ''
    for d in deps[:50]:
        rows += f'<tr><td style="font-family:monospace">{esc(d["name"])}</td><td>{esc(d.get("spec","*"))}</td><td>{esc(d.get("section",""))}</td></tr>'
    return f'''
    <div style="color:var(--text2);margin-bottom:8px">Package manager: <strong style="color:var(--text)">{esc(pm)}</strong> • {len(deps)} packages</div>
    <div class="table-wrap"><table>
      <thead><tr><th>Package</th><th>Version</th><th>Source</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    {f'<div style="margin-top:12px;color:var(--accent)">⚠️ {len(analysis["circular_deps"])} circular dependencies detected</div>' if analysis['circular_deps'] else ''}'''


def build_tree_html(tree, indent=0):
    lines = []
    sorted_keys = sorted(tree.keys())
    for key in sorted_keys:
        val = tree[key]
        prefix = '    ' * indent
        if isinstance(val, dict):
            lines.append(f'<span class="dir">{prefix}📁 {esc(key)}/</span>')
            lines.append(build_tree_html(val, indent + 1))
        else:
            lines.append(f'<span class="file">{prefix}📄 {esc(key)}</span> <span class="size">({val} lines)</span>')
    return '<br>'.join(lines)


def build_git_html(git_data):
    if not git_data:
        return '<div style="color:var(--text2)">No git repository found</div>'
    authors = git_data.get('authors', [])[:10]
    author_rows = ''.join(
        f'<tr><td>{esc(a["name"])}</td><td>{a["commits"]}</td><td>{a["commits"]/max(git_data["total_commits"],1)*100:.1f}%</td></tr>'
        for a in authors
    )
    active = git_data.get('active_files', [])[:10]
    file_rows = ''.join(
        f'<tr><td style="font-family:monospace;font-size:0.85em">{esc(f["file"])}</td><td>{f["commits"]}</td></tr>'
        for f in active
    )
    dr = git_data.get('date_range', {})
    br = git_data.get('branches', {})
    return f'''
    <div class="stats" style="margin-bottom:16px">
      <div class="stat-card"><div class="label">Total Commits</div><div class="value">{git_data.get("total_commits",0):,}</div></div>
      <div class="stat-card"><div class="label">Contributors</div><div class="value">{len(git_data.get("authors",[]))}</div></div>
      <div class="stat-card"><div class="label">Active Since</div><div class="value" style="font-size:1em">{esc(dr.get("first","?"))}</div></div>
      <div class="stat-card"><div class="label">Branch</div><div class="value" style="font-size:1em">{esc(br.get("current","?"))}</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div>
        <h3>Top Contributors</h3>
        <div class="table-wrap"><table><thead><tr><th>Author</th><th>Commits</th><th>Share</th></tr></thead><tbody>{author_rows}</tbody></table></div>
      </div>
      <div>
        <h3>Most Active Files</h3>
        <div class="table-wrap"><table><thead><tr><th>File</th><th>Commits</th></tr></thead><tbody>{file_rows}</tbody></table></div>
      </div>
    </div>'''


def _cos(deg):
    import math
    return 100 * math.cos(math.radians(deg))

def _sin(deg):
    import math
    return 100 * math.sin(math.radians(deg))

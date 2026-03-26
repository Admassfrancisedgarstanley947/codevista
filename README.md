<p align="center">
  <pre>
 ██████╗ ██████╗ ███╗   ██╗ ██████╗ ███████╗██╗ ██████╗ ██╗  ██╗████████╗
██╔═══██╗██╔══██╗████╗  ██║██╔════╝ ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
██║   ██║██████╔╝██╔██╗ ██║██║  ███╗███████╗██║██║  ███╗███████║   ██║
██║   ██║██╔══██╗██║╚██╗██║██║   ██║╚════██║██║██║   ██║██╔══██║   ██║
╚██████╔╝██║  ██║██║ ╚████║╚██████╔╝███████║██║╚██████╔╝██║  ██║   ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
  </pre>
</p>

<h3 align="center"><strong>Google Analytics for your code</strong></h3>
<p align="center">
  Beautiful interactive codebase visualizations — single HTML, zero dependencies.
</p>

---

## ✨ What is CodeVista?

CodeVista analyzes your codebase and generates a **stunning single-page HTML report** — no server, no internet, no external dependencies. Just share one file and everyone can explore your code visually.

## 🚀 Quick Start

```bash
pip install codevista
codevista analyze ./my-project/
```

That's it. Open `report.html` in any browser. No server needed.

## 📦 Installation

```bash
pip install codevista
```

Zero external dependencies — pure Python stdlib.

## 🎯 Commands

| Command | Description |
|---------|-------------|
| `codevista analyze ./project/` | Full analysis with all features |
| `codevista analyze ./project/ -o report.html` | Custom output path |
| `codevista analyze ./project/ --no-git` | Skip git analysis |
| `codevista analyze ./project/ --depth 3` | Limit directory depth |
| `codevista quick ./project/` | Fast analysis (~3 seconds) |
| `codevista serve ./project/ --port 8080` | Serve report on HTTP server |
| `codevista compare ./v1/ ./v2/` | Compare two codebases |
| `codevista watch ./project/` | Re-analyze on file changes |

## 📊 What It Analyyzes

### 🏗️ Architecture Map
- File dependency graph — who imports whom
- Interactive directory tree with line counts
- Module cluster detection

### 📈 Code Metrics
- Lines of code per file (interactive bar chart)
- Cyclomatic complexity (hot spot detection)
- Code duplication detection (hash-based)
- Comment coverage tracking
- File size distribution

### 🧩 Technology Detection
- Language detection (50+ languages)
- Framework detection (React, Django, Flask, Express, etc.)
- Dependency inventory with versions

### 🏥 Health Score
- Overall health: 0-100 (composite score)
- Per-category: readability, complexity, duplication, coverage, security, dependencies
- Color-coded indicators (green/yellow/red)
- Specific improvement recommendations

### 🔒 Security Scan
- Hardcoded secrets (AWS, GitHub, Stripe, API keys, passwords, tokens)
- Dangerous functions (eval, exec, shell=True, pickle)
- Private key detection
- Severity scoring (critical/high/medium/low)

### 👥 Git Insights
- Contribution heatmap (52-week calendar)
- Top contributors with commit share
- Most active files
- Commit statistics

## 🎨 Report Features

- **Single HTML file** — share anywhere, works offline forever
- **Dark/light mode** toggle
- **Interactive tables** — sort by any column, filter by language, search
- **Inline SVG charts** — no external JS libraries
- **Collapsible sections**
- **Print-friendly**
- **Responsive** — works on mobile

## 🏆 Comparison

| Feature | CodeVista | SonarQube | CodeClimate | lizard |
|---------|-----------|-----------|-------------|--------|
| Setup | `pip install` | Docker/Server | SaaS | `pip install` |
| Dependencies | **Zero** | Heavy | None | None |
| Output | **Single HTML** | Web UI | Web UI | CLI |
| Offline | ✅ | ❌ | ❌ | N/A |
| Security scan | ✅ | ✅ | ✅ | ❌ |
| Git analysis | ✅ | ✅ | ✅ | ❌ |
| Visual charts | ✅ | ✅ | ✅ | ❌ |
| Cost | **Free** | Free/Paid | Paid | Free |
| Server needed | **No** | Yes | Yes | No |

## 🏗️ Architecture

```
codevista/
├── cli.py           # CLI interface (argparse)
├── analyzer.py      # Core analysis engine
├── report.py        # HTML report generator
├── metrics.py       # Health scores & recommendations
├── security.py      # Secret/vulnerability scanning
├── dependencies.py  # Dependency parsing & analysis
├── git_analysis.py  # Git stats extraction
├── languages.py     # Language definitions & colors
├── config.py        # Configuration & ignore patterns
├── utils.py         # Utilities & color schemes
└── templates/       # HTML templates
```

## 🛠️ Tech Stack

- **Python 3.7+** (stdlib only)
- **Inline SVG** for all charts
- **CSS custom properties** for theming
- **Vanilla JavaScript** for interactivity

## 🤝 Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT © 2026 — see [LICENSE](LICENSE)

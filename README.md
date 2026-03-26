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
| `codevista smells ./project/` | Detect code smells and anti-patterns |
| `codevista architecture ./project/` | Detect architecture patterns |
| `codevista code-age ./project/` | Analyze file age, churn, and risk |
| `codevista export ./project/ -f sarif` | Export as SARIF for CI |
| `codevista export ./project/ --all` | Export to all formats |
| `codevista health ./project/` | Health score only |
| `codevista security ./project/` | Security scan only |
| `codevista deps ./project/` | Dependency analysis |
| `codevista git-stats ./project/` | Git repository statistics |
| `codevista languages ./project/` | Language distribution breakdown |
| `codevista complexity ./project/` | Complexity analysis and top functions |
| `codevista snapshot ./project/` | Save analysis snapshot for trend tracking |
| `codevista trends ./project/` | Show project health trends over time |
| `codevista diff-snapshots ./project/ 1 2` | Compare two snapshots |
| `codevista team ./project/` | Team productivity & collaboration analysis |
| `codevista ci-output ./project/ -f sarif` | CI/CD output (SARIF, Checkstyle, etc.) |

## 📊 What It Analyzes

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

### 👃 Code Smell Detection
CodeVista detects **19 categories of code smells** that go beyond typical linters:

| Smell | Description |
|-------|-------------|
| **God Classes** | Classes with too many methods/fields/responsibilities |
| **Long Parameter Lists** | Functions with too many params, especially with `=None` |
| **Feature Envy** | Methods using another class's data more than their own |
| **Divergent Change** | Classes modified for multiple unrelated reasons |
| **Shotgun Surgery** | Single logical change requiring edits across many files |
| **Parallel Inheritance** | Adding a subclass of A always requires subclassing B |
| **Speculative Generality** | Unused abstractions, abstract methods never overridden |
| **Temporary Fields** | Instance variables set only in certain methods |
| **Message Chains** | Long dot chains: `a.b.c.d.e.f` |
| **Middle Man** | Classes that only delegate to another class |
| **Comment Smells** | Comments describing WHAT code does, not WHY |
| **Dead Code** | Variables assigned but never read, functions never called |
| **Magic Numbers** | Unnamed numeric literals scattered in code |
| **Copy-Paste Code** | Near-duplicate blocks within and across files |
| **Missing Error Handling** | I/O operations without try/catch or error checks |
| **Inconsistent Naming** | Mixing camelCase and snake_case conventions |
| **Boolean Parameters** | Flags indicating method should be split |
| **isinstance Chains** | Type checking chains suggesting missing polymorphism |

Each smell comes with severity, location, and **actionable remediation advice**.

```bash
codevista smells ./my-project/
```

### 🏗️ Architecture Pattern Detection
Automatically identifies architectural patterns from project structure and code:

- **MVC / MVVM / MVP** — UI patterns
- **Layered Architecture** — presentation, business, data layers
- **Clean Architecture** — entities, use cases, controllers, adapters
- **Hexagonal** — ports & adapters pattern
- **Repository Pattern** — data access mediation
- **Service Layer** — application boundary with coordinating operations
- **CQRS** — command/query separation
- **Event-Driven** — event publishers, subscribers, handlers
- **Microservices** — independent service architecture
- **Singleton / Factory / Strategy / Observer / Decorator** — design patterns
- **Dependency Injection** — DI framework and manual injection

Includes architecture quality scoring (organization, coupling, modularity, balance) and text-based architecture diagrams.

```bash
codevista architecture ./my-project/
```

### 📅 Code Age & Risk Analysis
Track file age, change frequency, and identify files most likely to have bugs:

| Category | Description |
|----------|-------------|
| 🔥 **Hot** | Changed in the last 7 days |
| 🌤️ **Warm** | Changed in the last 30 days |
| ❄️ **Cold** | Changed 30-365 days ago |
| 🧊 **Cold Stable** | Old but few changes (stable) |
| 💀 **Dead** | Unchanged for >1 year |

**Risk Analysis** correlates age × complexity × churn to identify the files most likely to contain bugs:
- Files with high age, high complexity, and high change frequency get the highest risk scores
- Statistical correlation analysis between age, complexity, and churn
- Actionable recommendations for high-risk files

```bash
codevista code-age ./my-project/
```

## 📈 Trend Analysis

Track code quality over time with snapshots and trend visualization.

### How It Works

1. **Save snapshots** after each analysis run
2. **Compare snapshots** to see how your codebase evolves
3. **Get alerted** when metrics cross critical thresholds
4. **Track technical debt** ratio over time

```bash
# Save a snapshot of the current state
codevista snapshot ./my-project/

# Save with a label
codevista snapshot ./my-project/ --label "before-refactor"

# View trends
codevista trends ./my-project/

# Compare two specific snapshots
codevista diff-snapshots ./my-project/ 1 2
```

### ASCII Timeline Example

```
  📈 Health Score Timeline
  100 ┤████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
      │████████████████████
    0 ┤─────────────────────
  Current: 78/100 ↑
```

### Features

- **Trend arrows**: ↑ improving, ↓ degrading, → stable
- **Threshold alerts**: Get warned when health drops or security issues spike
- **Technical debt tracking**: Monitor debt ratio over time
- **Review cadence**: Suggests optimal review frequency based on change rate
- **Code age distribution**: Track how your codebase ages

## 👥 Team Metrics

Analyze developer productivity and collaboration patterns.

```bash
codevista team ./my-project/
```

### What It Analyzes

| Metric | Description |
|--------|-------------|
| **Lines per Author** | Added/removed/net per developer |
| **Commit Frequency** | Commits per day, burst vs steady patterns |
| **Files Touched** | Unique files per author |
| **Bus Factor** | People needed to understand 50% of code |
| **Code Ownership** | Pie chart data showing contribution share |
| **Review Coverage** | Estimate from commit messages |
| **Pair Programming** | Co-authored commit detection |
| **Time Zone Distribution** | When the team commits |
| **Onboarding Complexity** | How hard for a new contributor to ramp up |

## 📤 Export Formats

Export analysis results in multiple formats for different use cases:

| Format | Use Case | Command |
|--------|----------|---------|
| **HTML** | Interactive report in browser | `codevista export . -f html` |
| **JSON** | Programmatic access, APIs | `codevista export . -f json` |
| **Markdown** | Documentation, READMEs, wikis | `codevista export . -f markdown` |
| **SARIF** | GitHub Code Scanning, CI/CD | `codevista export . -f sarif` |
| **CSV** | Spreadsheets, data analysis | `codevista export . -f csv` |
| **YAML** | CODE_METRICS format | `codevista export . -f yaml` |
| **PDF** | Printable reports | `codevista export . -f pdf` |
| **All formats** | Everything at once | `codevista export . --all` |

```bash
# CI integration with GitHub Code Scanning
codevista export ./project/ -f sarif -o results.sarif.json

# Export everything
codevista export ./project/ -o ./reports/codevista --all
```

## 🔌 CI/CD Integration

CodeVista provides dedicated CI output formats with threshold-based pass/fail.

### Supported Formats

| Format | Platform | Command |
|--------|----------|---------|
| **SARIF** | GitHub Code Scanning | `codevista ci-output . -f sarif` |
| **GitLab Code Quality** | GitLab | `codevista ci-output . -f gitlab` |
| **Checkstyle XML** | Jenkins, GitHub Actions | `codevista ci-output . -f checkstyle` |
| **JUnit XML** | Any CI with JUnit support | `codevista ci-output . -f junit` |
| **Markdown** | PR comments | `codevista ci-output . -f markdown` |
| **Terminal** | Quick terminal output | `codevista ci-output . -f terminal` |

### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Clean | All thresholds passed |
| `1` | Warnings | Medium-severity threshold violations |
| `2` | Errors | High-severity violations (health, complexity) |
| `3` | Critical | Critical security issues or severe degradation |

### Threshold Configuration

Create `.codevista.json` in your project root:

```json
{
  "max_security_critical": 0,
  "max_security_high": 0,
  "max_security_medium": 5,
  "max_security_total": 10,
  "max_avg_complexity": 10,
  "max_technical_debt_ratio": 0.25,
  "min_health_score": 60,
  "max_duplicates": 10,
  "max_circular_deps": 0,
  "max_todo_count": 50
}
```

```bash
# Run with exit codes (CI will fail if thresholds violated)
codevista ci-output ./project/ -f sarif -o results.sarif.json
echo "Exit code: $?"  # 0=clean, 1=warnings, 2=errors, 3=critical
```

## 🐳 Docker

```bash
# Build
docker build -t codevista .

# Analyze a project
docker run --rm -v $(pwd):/workspace codevista analyze /workspace

# Use docker-compose
docker-compose up
```

The Docker image uses multi-stage builds for minimal size, runs as non-root, and includes `wkhtmltopdf` for PDF export.

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
| Code smell detection | ✅ **19 types** | Limited | Limited | ❌ |
| Architecture patterns | ✅ **12+ patterns** | ❌ | ❌ | ❌ |
| Code age analysis | ✅ | ❌ | ❌ | ❌ |
| SARIF export | ✅ | ✅ | ✅ | ❌ |
| Cost | **Free** | Free/Paid | Paid | Free |
| Server needed | **No** | Yes | Yes | No |

## 💎 What Makes CodeVista Unique

1. **Zero dependencies** — pure Python stdlib, no pip install headaches
2. **Single HTML output** — share one file, works offline forever, no server
3. **Deep code smell detection** — 19 smell categories with AST-level analysis, not just regex
4. **Architecture pattern detection** — identifies 12+ patterns from structure + code
5. **Code age × risk correlation** — statistical analysis of age, complexity, and churn
6. **Multi-format export** — HTML, JSON, Markdown, SARIF, CSV, YAML, PDF
7. **Docker support** — multi-stage build, non-root user, PDF-ready
8. **Beautiful design** — dark mode, glassmorphism, inline SVG charts, animations
9. **Works on any codebase** — 50+ languages, no configuration needed
10. **CI/CD ready** — SARIF export for GitHub Code Scanning integration

## 🏗️ Architecture

```
codevista/
├── cli.py            # CLI interface (argparse)
├── analyzer.py       # Core analysis engine
├── report.py         # HTML report generator
├── metrics.py        # Health scores & recommendations
├── smells.py         # Code smell detection (19 categories)
├── architecture.py   # Architecture pattern detector
├── code_age.py       # Code age & risk analysis
├── export.py         # Multi-format export (HTML/JSON/MD/SARIF/CSV/YAML/PDF)
├── security.py       # Secret/vulnerability scanning
├── dependencies.py   # Dependency parsing & analysis
├── git_analysis.py   # Git stats extraction
├── trends.py         # Trend analysis & snapshot tracking
├── team.py           # Team metrics & collaboration analysis
├── integrations.py   # CI/CD output (SARIF, Checkstyle, JUnit, GitLab)
├── languages.py      # Language definitions & colors
├── config.py         # Configuration & ignore patterns
├── utils.py          # Utilities & color schemes
└── templates/        # HTML templates
```

## 🛠️ Tech Stack

- **Python 3.7+** (stdlib only)
- **Inline SVG** for all charts
- **CSS custom properties** for theming
- **Vanilla JavaScript** for interactivity
- **AST parsing** for deep code analysis (Python)

## 🤝 Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT © 2026 — see [LICENSE](LICENSE)

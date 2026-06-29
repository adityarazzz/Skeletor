import json
from pathlib import Path
from typing import Dict, Any
import networkx as nx

def export_all(graph: nx.DiGraph, report_md: str, diagrams: Dict[str, str], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Report
    with open(out_dir / "ARCHITECTURE_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_md)
        
    # 2. Diagrams
    for name, content in diagrams.items():
        if name.startswith("_"):
            continue
        with open(out_dir / f"{name}.mmd", "w", encoding="utf-8") as f:
            f.write(content)
            
    # 3. JSON Model
    node_link = nx.node_link_data(graph)
    with open(out_dir / "model.json", "w", encoding="utf-8") as f:
        json.dump(node_link, f, indent=2)
        
    # 4. Compute stats
    total_files = len([n for n, d in graph.nodes(data=True) if d.get('type') == 'module'])
    total_entities = len(graph.nodes)
    total_deps = len(graph.edges)
    total_layers = len([name for name, nodes in diagrams.get('_layer_data', {}).items() if nodes]) if '_layer_data' in diagrams else 0

    # 5. HTML Dashboard
    safe_report_md = json.dumps(report_md)
    arch_diagram = diagrams.get('architecture', 'graph TD\nEmpty')
    dep_diagram = diagrams.get('dependencies', 'graph TD\nEmpty')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skeletor — Architecture</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <style>
        :root {{
            --bg-base: #000000;
            --bg-panel: #0A0A0A;
            --bg-surface: #121212;
            --bg-surface-hover: #1A1A1A;
            --border: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(255, 255, 255, 0.15);
            --text-primary: #F2F2F2;
            --text-secondary: #8A8A8A;
            --text-tertiary: #5C5C5C;
            --accent: #E2E2E2;
            --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.5);
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 8px;
            --transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-base);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--bg-surface-hover); border-radius: 4px; border: 2px solid var(--bg-base); }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-tertiary); }}

        /* --- HEADER --- */
        .header {{
            height: 64px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            border-bottom: 1px solid var(--border);
            background: var(--bg-base);
            z-index: 10;
        }}

        .brand {{
            font-size: 14px;
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .brand::before {{
            content: '';
            width: 16px;
            height: 16px;
            border-radius: 4px;
            background: linear-gradient(135deg, #FFF 0%, #888 100%);
        }}

        .meta {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-tertiary);
        }}

        /* --- SEGMENTED CONTROL (TABS) --- */
        .segmented-control {{
            display: flex;
            background: var(--bg-panel);
            padding: 4px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            gap: 4px;
        }}
        .segment {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 13px;
            font-weight: 500;
            padding: 6px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: var(--transition);
        }}
        .segment:hover {{ color: var(--text-primary); }}
        .segment.active {{
            background: var(--bg-surface-hover);
            color: var(--text-primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}

        /* --- MAIN CONTENT --- */
        .main-content {{
            flex: 1;
            overflow: hidden;
            position: relative;
        }}

        .tab-pane {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease;
            overflow-y: auto;
            padding: 32px;
        }}
        .tab-pane.active {{
            opacity: 1;
            visibility: visible;
        }}

        /* --- BENTO GRID (OVERVIEW) --- */
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .bento-box {{
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), var(--shadow-sm);
            transition: var(--transition);
        }}
        .bento-box:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }}

        .stat-label {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
        }}
        .stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            font-weight: 400;
            color: var(--text-primary);
            letter-spacing: -0.03em;
        }}

        .report-box {{
            grid-column: span 4;
            min-height: 400px;
        }}

        /* --- CANVAS PANE (DIAGRAMS) --- */
        .canvas-pane {{
            padding: 0;
            display: flex;
            flex-direction: column;
        }}
        .canvas-header {{
            position: absolute;
            top: 24px;
            left: 24px;
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 12px 16px;
            z-index: 20;
            display: flex;
            flex-direction: column;
            gap: 4px;
            box-shadow: var(--shadow-sm);
        }}
        .canvas-title {{ font-size: 14px; font-weight: 600; }}
        .canvas-subtitle {{ font-size: 12px; color: var(--text-secondary); }}
        
        .canvas-body {{
            flex: 1;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at center, var(--bg-panel) 0%, var(--bg-base) 100%);
        }}

        /* --- MARKDOWN STYLES --- */
        .markdown-body {{
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.6;
        }}
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.75em;
            letter-spacing: -0.01em;
        }}
        .markdown-body h1 {{ font-size: 20px; }}
        .markdown-body h2 {{ font-size: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        .markdown-body p {{ margin-bottom: 1em; color: var(--text-secondary); }}
        .markdown-body strong {{ color: var(--text-primary); }}
        .markdown-body ul {{ margin-left: 20px; margin-bottom: 1em; color: var(--text-secondary); }}
        .markdown-body li {{ margin-bottom: 4px; }}
        .markdown-body code {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-surface);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            border: 1px solid var(--border);
            color: var(--accent);
        }}
        .markdown-body pre code {{
            display: block;
            padding: 16px;
            overflow-x: auto;
            border-radius: var(--radius-sm);
            line-height: 1.5;
        }}

    </style>
</head>
<body>

    <!-- Header -->
    <header class="header">
        <div class="brand">Skeletor</div>
        
        <nav class="segmented-control">
            <button class="segment active" onclick="switchTab('overview')">Overview</button>
            <button class="segment" onclick="switchTab('architecture')">Layer Map</button>
            <button class="segment" onclick="switchTab('dependencies')">Dependencies</button>
        </nav>

        <div class="meta">Analysis v1.0</div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
        
        <!-- Tab: Overview -->
        <div id="tab-overview" class="tab-pane active">
            <div class="bento-grid">
                <div class="bento-box">
                    <span class="stat-label">Source Files</span>
                    <span class="stat-value">{total_files}</span>
                </div>
                <div class="bento-box">
                    <span class="stat-label">Entities</span>
                    <span class="stat-value">{total_entities}</span>
                </div>
                <div class="bento-box">
                    <span class="stat-label">Dependencies</span>
                    <span class="stat-value">{total_deps}</span>
                </div>
                <div class="bento-box">
                    <span class="stat-label">Arch Layers</span>
                    <span class="stat-value">{total_layers}</span>
                </div>
                
                <div class="bento-box report-box">
                    <div id="markdown-container" class="markdown-body"></div>
                </div>
            </div>
        </div>

        <!-- Tab: Architecture -->
        <div id="tab-architecture" class="tab-pane canvas-pane">
            <div class="canvas-header">
                <div class="canvas-title">Layer Map</div>
                <div class="canvas-subtitle">Interactive block diagram · Scroll to zoom</div>
            </div>
            <div class="canvas-body">
                <div class="mermaid" style="width:100%;height:100%">
{arch_diagram}
                </div>
            </div>
        </div>

        <!-- Tab: Dependencies -->
        <div id="tab-dependencies" class="tab-pane canvas-pane">
            <div class="canvas-header">
                <div class="canvas-title">Dependency Graph</div>
                <div class="canvas-subtitle">Module coupling map · Scroll to zoom</div>
            </div>
            <div class="canvas-body">
                <div class="mermaid" style="width:100%;height:100%">
{dep_diagram}
                </div>
            </div>
        </div>

    </main>

    <!-- Scripts -->
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose',
            fontFamily: 'Inter, sans-serif'
        }});

        // Render Markdown Report
        const reportData = {safe_report_md};
        document.getElementById('markdown-container').innerHTML = marked.parse(reportData);

        // Setup Pan/Zoom after mermaid renders
        setTimeout(() => {{
            document.querySelectorAll('.mermaid svg').forEach(svg => {{
                svg.style.width = '100%';
                svg.style.height = '100%';
                svg.style.maxWidth = '100%';
                svgPanZoom(svg, {{
                    zoomEnabled: true,
                    controlIconsEnabled: false,
                    fit: true,
                    center: true,
                    minZoom: 0.1,
                    maxZoom: 10,
                    zoomScaleSensitivity: 0.2
                }});
            }});
        }}, 600);
    </script>
    <script>
        function switchTab(tabId) {{
            // Hide all panes
            document.querySelectorAll('.tab-pane').forEach(t => t.classList.remove('active'));
            // Deactivate all segments
            document.querySelectorAll('.segment').forEach(t => t.classList.remove('active'));
            
            // Activate selected
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
    with open(out_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)

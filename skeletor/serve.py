from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from pathlib import Path
from skeletor.scan import scan
from skeletor.parse import parse
from skeletor.model import build_model
from skeletor.layer import detect_layers
from skeletor.analyze import analyze_metrics
from skeletor.diagram import generate_diagrams
from skeletor.report import generate_report
from skeletor.export import export_all

app = FastAPI(title="Skeletor MCP Server", description="MCP Server for deep codebase understanding")

class ScanRequest(BaseModel):
    path: str

@app.post("/analyze")
def analyze_path(req: ScanRequest):
    """Trigger a full analysis pipeline."""
    target = Path(req.path).resolve()
    if not target.exists():
        return {"error": "Path not found"}
        
    scan_result = scan(target)
    
    parse_results = []
    for f in scan_result["files"]:
        parse_results.append(parse(f))
        
    graph = build_model(parse_results)
    layers = detect_layers(graph)
    metrics = analyze_metrics(graph)
    diagrams = generate_diagrams(graph, layers)
    report_md = generate_report(graph, layers, metrics, diagrams)
    
    out_dir = target / "skeletor-out"
    export_all(graph, report_md, diagrams, out_dir)
    
    return {
        "status": "success",
        "scanned_files": len(scan_result["files"]),
        "report_path": str(out_dir / "ARCHITECTURE_REPORT.md"),
        "dashboard_path": str(out_dir / "dashboard.html")
    }

def start_server(host="127.0.0.1", port=8000):
    uvicorn.run(app, host=host, port=port)

import argparse
import sys
from pathlib import Path
from skeletor.scan import scan
from skeletor.parse import parse
from skeletor.model import build_model
from skeletor.layer import detect_layers
from skeletor.analyze import analyze_metrics
from skeletor.diagram import generate_diagrams
from skeletor.report import generate_report
from skeletor.export import export_all

def main():
    parser = argparse.ArgumentParser(prog="skeletor", description="Skeletor - Deep codebase understanding")
    parser.add_argument("path", nargs="?", default=".", help="Path to analyze")
    parser.add_argument("--update", action="store_true", help="Only update changed files")
    
    args = parser.parse_args()
    
    target_path = Path(args.path).resolve()
    
    print(f"Scanning {target_path}...")
    scan_result = scan(target_path)
    print(f"Found {len(scan_result['files'])} files. (Ignored: {scan_result['ignored_count']}, Sensitive: {scan_result['sensitive_count']})")
    
    print("Parsing AST...")
    parse_results = []
    for f in scan_result["files"]:
        parse_results.append(parse(f))
        
    print("Building model...")
    graph = build_model(parse_results)
    
    print("Detecting layers...")
    layers = detect_layers(graph)
    
    print("Analyzing metrics...")
    metrics = analyze_metrics(graph)
    
    print("Generating diagrams...")
    diagrams = generate_diagrams(graph, layers)
    
    print("Generating report...")
    report_md = generate_report(graph, layers, metrics, diagrams)
    
    print("Exporting results...")
    out_dir = target_path / "skeletor-out"
    export_all(graph, report_md, diagrams, out_dir)
    
    print(f"Done! Results saved to {out_dir}")

    
if __name__ == "__main__":
    sys.exit(main())

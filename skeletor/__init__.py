"""
Skeletor - Deep codebase understanding and architecture visualization tool.
"""

def __getattr__(name):
    _map = {
        "scan": ("skeletor.scan", "scan"),
        "parse": ("skeletor.parse", "parse"),
        "build_model": ("skeletor.model", "build_model"),
        "detect_layers": ("skeletor.layer", "detect_layers"),
        "analyze_metrics": ("skeletor.analyze", "analyze_metrics"),
        "generate_diagrams": ("skeletor.diagram", "generate_diagrams"),
        "generate_report": ("skeletor.report", "generate_report"),
        "export_all": ("skeletor.export", "export_all"),
    }
    if name in _map:
        import importlib
        module_name, func_name = _map[name]
        module = importlib.import_module(module_name)
        return getattr(module, func_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

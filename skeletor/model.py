import networkx as nx
from typing import List, Dict, Any

class CodeModel:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def build(self, parse_results: List[Dict[str, Any]]):
        for result in parse_results:
            file_path = result["file"]
            self.graph.add_node(file_path, type="module", extension=result["extension"])
            
            for cls in result.get("classes", []):
                cls_id = f"{file_path}::{cls}"
                self.graph.add_node(cls_id, type="class", name=cls)
                self.graph.add_edge(file_path, cls_id, relation="contains")
                
            for func in result.get("functions", []):
                func_id = f"{file_path}::{func}"
                self.graph.add_node(func_id, type="function", name=func)
                self.graph.add_edge(file_path, func_id, relation="contains")
                
            for imp in result.get("imports", []):
                # We add the import as a raw string node. A proper resolution phase
                # would link this to the actual module node.
                imp_id = f"import::{imp}"
                if not self.graph.has_node(imp_id):
                    self.graph.add_node(imp_id, type="import", name=imp)
                self.graph.add_edge(file_path, imp_id, relation="imports")

def build_model(parse_results: List[Dict[str, Any]]) -> nx.DiGraph:
    model = CodeModel()
    model.build(parse_results)
    return model.graph

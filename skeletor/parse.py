import tree_sitter
import tree_sitter_python
from pathlib import Path
from typing import Dict, Any, List

def _parse_python(file_path: Path, content: bytes) -> Dict[str, Any]:
    lang = tree_sitter.Language(tree_sitter_python.language())
    parser = tree_sitter.Parser(lang)
    tree = parser.parse(content)
    
    classes = []
    functions = []
    imports = []
    
    # A simple AST traversal for Python
    def traverse(node):
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(content[name_node.start_byte:name_node.end_byte].decode("utf8"))
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append(content[name_node.start_byte:name_node.end_byte].decode("utf8"))
        elif node.type == "import_statement" or node.type == "import_from_statement":
            imports.append(content[node.start_byte:node.end_byte].decode("utf8"))
            
        for child in node.children:
            traverse(child)
            
    traverse(tree.root_node)
    
    return {
        "classes": classes,
        "functions": functions,
        "imports": imports,
    }

def parse(file_path: Path) -> Dict[str, Any]:
    """Parse a file to extract its AST symbols."""
    with open(file_path, "rb") as f:
        content = f.read()
        
    ext = file_path.suffix.lower()
    
    result = {
        "classes": [],
        "functions": [],
        "imports": []
    }
    
    try:
        if ext == ".py":
            result = _parse_python(file_path, content)
        # TODO: Add other languages (TS, JS, Go, Rust, Java, etc.)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        
    return {
        "file": str(file_path),
        "extension": ext,
        **result
    }

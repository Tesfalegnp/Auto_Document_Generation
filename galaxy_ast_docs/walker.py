# galaxy_ast_docs/walker.py
import os
import logging
from .language_layer import detect_language, get_parser, is_metta_language
from .parser_layer import parse_code
from .traversal_layer import extract_definitions

def build_tree(root_path, debug=False):
    """Recursively builds folder/file tree with AST info for code files."""
    def process_path(path):
        if os.path.isdir(path):
            return {
                "name": os.path.basename(path),
                "path": os.path.abspath(path),
                "type": "folder",
                "children": [process_path(os.path.join(path, child))
                             for child in sorted(os.listdir(path))
                             if not child.startswith('.')]
            }
        else:
            file_info = {
                "name": os.path.basename(path),
                "path": os.path.abspath(path),
                "type": "file"
            }
            
            # Detect language
            lang = detect_language(path)
            if lang:
                try:
                    # Read file content
                    with open(path, "rb") as f:
                        code_bytes = f.read()
                    
                    # Get appropriate parser
                    parser = get_parser(lang)
                    
                    # Parse code (handles both Tree-sitter and MeTTa)
                    tree = parse_code(parser, code_bytes)
                    
                    # Extract definitions
                    definitions = extract_definitions(tree, code_bytes, lang)
                    
                    # Update file info
                    file_info.update({
                        "language": lang,
                        "definitions": definitions
                    })
                    
                    # Add MeTTa-specific metadata
                    if is_metta_language(lang):
                        file_info["parser_type"] = "custom_metta"
                    else:
                        file_info["parser_type"] = "tree_sitter"
                        
                except Exception as e:
                    if debug:
                        logging.error(f"Error parsing {path}: {e}")
                    # Add error info to file_info
                    file_info["parse_error"] = str(e)
                    
            return file_info

    return process_path(root_path)

def walk_and_parse(root_path, debug=False):
    """Main entry point for walking and parsing directory tree"""
    return build_tree(root_path, debug)

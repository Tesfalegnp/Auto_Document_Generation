# galaxy_ast_docs/parser_layer.py
from .language_layer import is_metta_language
from .metta_parser import create_metta_parser

def parse_code(parser, code_bytes):
    """Parse code using appropriate parser"""
    # Handle MeTTa with custom parser
    if parser is None:
        # Assume this is MeTTa language
        metta_parser = create_metta_parser()
        return metta_parser.parse(code_bytes)
    
    # Handle standard Tree-sitter languages
    return parser.parse(code_bytes)
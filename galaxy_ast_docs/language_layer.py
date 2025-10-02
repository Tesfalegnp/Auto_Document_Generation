# galaxy_ast_docs/language_layer.py
import os
import re
from tree_sitter import Language, Parser

HERE = os.path.dirname(__file__)
BUILD_DIR = os.path.join(HERE, "build")
LIB_PATH = os.path.join(BUILD_DIR, "my-languages.so")

# Standard Tree-sitter parsers
PARSERS = {
    "python": "tree-sitter-python",
    "javascript": "tree-sitter-javascript", 
    "java": "tree-sitter-java",
} 

# Extension mapping including MeTTa
EXT_MAP = {
    ".py": "python",
    ".js": "javascript", 
    ".java": "java",
    ".metta": "metta",
    ".mta": "metta",
}

_LANGS = {}

def _ensure_built():
    """Ensure Tree-sitter library is built for standard languages"""
    if not os.path.exists(LIB_PATH):
        # Only check for standard parsers, MeTTa uses custom implementation
        standard_langs = [k for k in PARSERS.keys()]
        if any(detect_language(f"test.{ext[1:]}") in standard_langs for ext in EXT_MAP if EXT_MAP[ext] in standard_langs):
            raise RuntimeError(
                f"Tree-sitter language library not found at: {LIB_PATH}\n"
                "Please build it by running:\n"
                "  python -m galaxy_ast_docs.build_parsers\n"
            )

def _load_languages():
    """Load Tree-sitter languages (excluding MeTTa which uses custom parser)"""
    _ensure_built()
    for name in PARSERS.keys():
        if name in _LANGS:
            continue
        try:
            _LANGS[name] = Language(LIB_PATH, name)
        except Exception as e:
            raise RuntimeError(f"Failed to load language '{name}': {e}")

def get_parser(lang_name):
    """Get parser for specified language"""
    if lang_name == "metta":
        # Return None for MeTTa - we'll handle it with custom parser
        return None
    
    if lang_name not in _LANGS:
        _load_languages()
    parser = Parser()
    parser.set_language(_LANGS[lang_name])
    return parser

def detect_language(file_path):
    """Detect programming language from file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_MAP.get(ext)

def available_languages():
    """Return list of supported languages"""
    return list(set(EXT_MAP.values()))

def get_language_version(lang_name):
    """Get the version of the loaded language parser"""
    if lang_name == "metta":
        return "custom-1.0"
    
    _load_languages()
    if lang_name in _LANGS:
        return _LANGS[lang_name].version
    return None

def is_metta_language(lang_name):
    """Check if language is MeTTa"""
    return lang_name == "metta"
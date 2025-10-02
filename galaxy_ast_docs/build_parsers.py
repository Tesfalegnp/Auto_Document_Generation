# galaxy_ast_docs/build_parsers.py
import os
import sys
from pathlib import Path
import tree_sitter

BASE_DIR = Path(__file__).resolve().parent
BUILD_DIR = BASE_DIR / "build"
PARSERS_DIR = BASE_DIR / "parsers"
LIB_PATH = BUILD_DIR / "my-languages.so"

LANGUAGES = {
    "python": PARSERS_DIR / "tree-sitter-python",
    "javascript": PARSERS_DIR / "tree-sitter-javascript",
    "java": PARSERS_DIR / "tree-sitter-java",
}

def main():
    print("=== Building Tree-sitter languages ===")
    
    # Verify tree-sitter installation
    try:
        from tree_sitter import Language
    except ImportError:
        print("ERROR: tree_sitter module not installed")
        print("Please run: pip install tree_sitter==0.22.1 #you can change version")
        sys.exit(1)
    
    # Check build method exists
    if not hasattr(Language, 'build_library'):
        print("ERROR: Language.build_library method missing!")
        print("This usually means an incompatible tree-sitter version is installed")
        print("Try reinstalling with: pip install --force-reinstall tree_sitter")
        sys.exit(1)
    
    # Create directories
    BUILD_DIR.mkdir(exist_ok=True)
    
    # Verify parser directories
    missing_parsers = [lang for lang, path in LANGUAGES.items() if not path.exists()]
    if missing_parsers:
        print("\nERROR: Missing parser directories:")
        for lang in missing_parsers:
            print(f"  - {lang}: {LANGUAGES[lang]}")
        print("\nPlease clone the repositories with:")
        print("cd galaxy_ast_docs/parsers")
        for lang in missing_parsers:
            print(f"git clone https://github.com/tree-sitter/tree-sitter-{lang}")
        sys.exit(1)
    
    # Build library
    try:
        print(f"Building library: {LIB_PATH}")
        Language.build_library(
            str(LIB_PATH),
            [str(path) for path in LANGUAGES.values()]
        )
        print(f"✅ Build complete: {LIB_PATH}")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure you have build tools installed:")
        print("   Ubuntu: sudo apt install build-essential python3-dev")
        print("   macOS: xcode-select --install")
        print("2. Try clean reinstall: pip install --force-reinstall tree_sitter")
        print("3. Check parser repos are complete")
        sys.exit(1)

if __name__ == "__main__":
    main()
  
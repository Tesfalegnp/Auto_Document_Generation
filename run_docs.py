#!/usr/bin/env python3
"""
Robust end-to-end documentation generator.

Usage:
  python run_docs.py --root /path/to/any/project

This script will:
  1) Build parsers
  2) Generate AST JSON
  3) Generate README with LLM
  4) Convert README -> HTML (if tools/md_to_html.py exists)

It will try several common flag-name variants for each step (so helper scripts
that use --json / --root or --out / --output are supported).
"""
from pathlib import Path
import argparse
import subprocess
import sys
import os

PROJECT_ROOT = Path(__file__).parent.resolve()
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

AST_JSON = DOCS_DIR / "ast_summary.json"
README_MD = PROJECT_ROOT / "README_docs.md"
INDEX_HTML = DOCS_DIR / "index.html"


def _display_cmd(cmd):
    try:
        return " ".join(cmd)
    except Exception:
        return str(cmd)


def try_variants(variants, cwd, desc):
    """Try a list of command variants until one succeeds; exit on total failure."""
    print(f"\n🚀 {desc}")
    last_errors = []
    for cmd in variants:
        print(f"   $ {_display_cmd(cmd)}")
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        except FileNotFoundError as e:
            print(f"   ❌ Failed (not found): {e}")
            last_errors.append((cmd, str(e)))
            continue

        if result.returncode == 0:
            if result.stdout:
                print(result.stdout.strip())
            print("   ✅ Success")
            return result
        else:
            stderr = (result.stderr or result.stdout or "").strip()
            print(f"   ❌ Variant failed: {stderr}")
            last_errors.append((cmd, stderr))
    # all failed
    print(f"\n❌ All variants for: {desc} failed. Summary of attempts:")
    for cmd, err in last_errors:
        print(f" - {_display_cmd(cmd)} -> {err[:400]}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate full docs from project root.")
    parser.add_argument("--root", required=True, help="Path to source code project (e.g., ./my_project)")
    parser.add_argument("--no-open", action="store_true", help="Don't try to open the generated HTML in a browser")
    args = parser.parse_args()

    target_root = Path(args.root).resolve()
    if not target_root.exists():
        print(f"❌ Project root not found: {target_root}", file=sys.stderr)
        sys.exit(1)

    print(f"📁 Analyzing project: {target_root}")

    # Step 1: Build parsers (idempotent)
    build_variants = [
        [sys.executable, "-m", "galaxy_ast_docs.build_parsers"],
        [sys.executable, str(PROJECT_ROOT / "galaxy_ast_docs" / "build_parsers.py")]
    ]
    try_variants(build_variants, cwd=PROJECT_ROOT, desc="1. Building language parsers...")

    # Step 2: Generate AST JSON
    gen_ast_variants = [
        [sys.executable, "-m", "galaxy_ast_docs.generate_ast_docs", "--root", str(target_root), "--output", str(AST_JSON)],
        [sys.executable, "-m", "galaxy_ast_docs.generate_ast_docs", "--root", str(target_root), "--out", str(AST_JSON)],
        [sys.executable, str(PROJECT_ROOT / "galaxy_ast_docs" / "generate_ast_docs.py"), "--root", str(target_root), "--output", str(AST_JSON)],
        [sys.executable, str(PROJECT_ROOT / "galaxy_ast_docs" / "generate_ast_docs.py"), "--root", str(target_root), "--out", str(AST_JSON)],
    ]
    try_variants(gen_ast_variants, cwd=PROJECT_ROOT, desc="2. Parsing code into AST...")

    # Step 3: Generate README with LLM
    # Many helper scripts accept either --json or --root for input and --out/--output for destination.
    gen_readme_variants = [
        [sys.executable, "-m", "llm.generate_readme", "--json", str(AST_JSON), "--out", str(README_MD)],
        [sys.executable, "-m", "llm.generate_readme", "--json", str(AST_JSON), "--output", str(README_MD)],
        [sys.executable, "-m", "llm.generate_readme", "--root", str(target_root), "--out", str(README_MD)],
        [sys.executable, "-m", "llm.generate_readme", "--root", str(target_root), "--output", str(README_MD)],
        [sys.executable, str(PROJECT_ROOT / "llm" / "generate_readme.py"), "--json", str(AST_JSON), "--out", str(README_MD)],
        [sys.executable, str(PROJECT_ROOT / "llm" / "generate_readme.py"), "--json", str(AST_JSON), "--output", str(README_MD)],
        [sys.executable, str(PROJECT_ROOT / "llm" / "generate_readme.py"), "--root", str(target_root), "--out", str(README_MD)],
        [sys.executable, str(PROJECT_ROOT / "llm" / "generate_readme.py"), "--root", str(target_root), "--output", str(README_MD)],
    ]
    try_variants(gen_readme_variants, cwd=PROJECT_ROOT, desc="3. Generating README with LLM...")

    # Step 4: Convert to HTML (if the tool exists)
    md_to_html_path = PROJECT_ROOT / "tools" / "md_to_html.py"
    if not md_to_html_path.exists():
        print("⚠️  tools/md_to_html.py not found. Skipping HTML conversion.")
        print(f"📄 README available at: {README_MD}")
    else:
        md_variants = [
            [sys.executable, "-m", "tools.md_to_html", "--md", str(README_MD), "--out", str(INDEX_HTML)],
            [sys.executable, "-m", "tools.md_to_html", "--md", str(README_MD), "--output", str(INDEX_HTML)],
            [sys.executable, str(md_to_html_path), "--md", str(README_MD), "--out", str(INDEX_HTML)],
            [sys.executable, str(md_to_html_path), "--md", str(README_MD), "--output", str(INDEX_HTML)],
        ]
        try_variants(md_variants, cwd=PROJECT_ROOT, desc="4. Converting README to HTML...")

        # Open in browser (best-effort)
        if not args.no_open:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(INDEX_HTML)])
                elif sys.platform.startswith("linux"):
                    subprocess.run(["xdg-open", str(INDEX_HTML)])
                elif sys.platform == "win32":
                    os.startfile(str(INDEX_HTML))
                print(f"\n✅ Docs ready! Opened: {INDEX_HTML}")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"📄 View manually: file://{INDEX_HTML}")


if __name__ == "__main__":
    main()

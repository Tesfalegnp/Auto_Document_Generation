#!/usr/bin/env python3
"""
End-to-end documentation generator.

Usage:
  python run_docs.py --root /path/to/any/project

Features:
  - Invokes module scripts via `python -m ...`
  - Detects whether modules accept --root by running `--help` (safe probe)
  - Prints helpful output and shows stderr on failure for debugging
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from shutil import which

PROJECT_ROOT = Path(__file__).parent.resolve()
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

AST_JSON = DOCS_DIR / "ast_summary.json"
README_MD = PROJECT_ROOT / "README_docs.md"
INDEX_HTML = DOCS_DIR / "index.html"


def run_cmd(cmd, cwd=None, desc=""):
    """
    Run cmd (list or str). Print header and command.
    Return subprocess.CompletedProcess.
    On non-zero exit, print stdout/stderr and exit(1).
    """
    print(f"\n🚀 {desc}")
    if isinstance(cmd, list):
        pretty = " ".join(map(str, cmd))
    else:
        pretty = str(cmd)
    print(f"   $ {pretty}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Failed (exit {result.returncode}). stderr:\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def module_accepts_arg(module_name: str, arg: str, cwd: Path) -> bool:
    """
    Probe `python -m module_name --help` to check if help output mentions `arg`.
    Returns True if seen, False otherwise.
    This avoids passing unknown args to modules that don't accept them.
    """
    try:
        p = subprocess.run([sys.executable, "-m", module_name, "--help"],
                           cwd=cwd, capture_output=True, text=True, timeout=10)
        help_out = (p.stdout or "") + (p.stderr or "")
        return arg in help_out
    except Exception:
        # If probe fails (timeout / crash), be conservative and return False
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate full docs from project root.")
    parser.add_argument("--root", required=True,
                        help="Path to source code project (e.g., ./my_project)")
    parser.add_argument("--skip-build", action="store_true", help="Skip building parsers step")
    parser.add_argument("--no-open", action="store_true", help="Don't attempt to open generated HTML")
    args = parser.parse_args()

    target_root = Path(args.root).resolve()
    if not target_root.exists():
        print(f"❌ Project root not found: {target_root}", file=sys.stderr)
        sys.exit(1)

    print(f"📁 Analyzing project: {target_root}")

    # Use PROJECT_ROOT as cwd for module runs so relative packages are found
    cwd = PROJECT_ROOT

    # Step 1: Build parsers (idempotent)
    if not args.skip_build:
        build_module = "galaxy_ast_docs.build_parsers"
        # If this module accepts --root, pass it; otherwise just run module
        cmd = [sys.executable, "-m", build_module]
        if module_accepts_arg(build_module, "--root", cwd):
            cmd += ["--root", str(target_root)]
        run_cmd(cmd, cwd=cwd, desc="1. Building language parsers...")

    # Step 2: Generate AST JSON
    gen_ast_module = "galaxy_ast_docs.generate_ast_docs"
    cmd = [sys.executable, "-m", gen_ast_module,
           "--root", str(target_root),
           "--output", str(AST_JSON)]
    run_cmd(cmd, cwd=cwd, desc="2. Parsing code into AST...")

    # Step 3: Generate README with LLM
    llm_module = "llm.generate_readme"
    llm_cmd = [sys.executable, "-m", llm_module,
               "--json", str(AST_JSON),
               "--out", str(README_MD)]
    # Only add --root if the module advertises it in help
    if module_accepts_arg(llm_module, "--root", cwd):
        llm_cmd[3:3] = ["--root", str(target_root)]  # insert before the rest
        # (we insert at position 3 to keep ordering readable)
    run_cmd(llm_cmd, cwd=cwd, desc="3. Generating README with LLM...")

    # Step 4: Convert to HTML (if tools/md_to_html.py exists)
    md_to_html_path = PROJECT_ROOT / "tools" / "md_to_html.py"
    if not md_to_html_path.exists():
        print("⚠️  tools/md_to_html.py not found. Skipping HTML conversion.")
    else:
        md_module = "tools.md_to_html"
        md_cmd = [sys.executable, "-m", md_module,
                  "--md", str(README_MD),
                  "--out", str(INDEX_HTML)]
        if module_accepts_arg(md_module, "--root", cwd):
            md_cmd[3:3] = ["--root", str(target_root)]
        run_cmd(md_cmd, cwd=cwd, desc="4. Converting README to HTML...")

        # Open in browser (Linux/macOS/Windows)
        if not args.no_open:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(INDEX_HTML)])
                elif sys.platform.startswith("linux"):
                    # prefer xdg-open if available
                    if which("xdg-open"):
                        subprocess.run(["xdg-open", str(INDEX_HTML)])
                    else:
                        print("⚠️  xdg-open not available; skipping auto-open.")
                elif sys.platform == "win32":
                    os.startfile(str(INDEX_HTML))
                print(f"\n✅ Docs ready! Opened: {INDEX_HTML}")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"📄 View manually: file://{INDEX_HTML}")

    print("\n🏁 Done.")


if __name__ == "__main__":
    main()

"""
Generate a deep, file-by-file README from AST JSON using Gemini.
"""

import argparse
from pathlib import Path
from llm.llm_integration import generate_from_json_file


def main():
    parser = argparse.ArgumentParser(description="Generate deep README from AST JSON.")
    parser.add_argument("--json", required=True, help="Path to AST JSON (e.g., docs/ast_summary.json)")
    parser.add_argument("--out", default="README_docs.md", help="Output README file")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Gemini model")
    args = parser.parse_args()

    try:
        md_content = generate_from_json_file(args.json, model=args.model)
        out_path = Path(args.out)
        out_path.write_text(md_content, encoding="utf-8")
        print(f"✅ Deep README generated: {out_path.resolve()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        raise


if __name__ == "__main__":
    main()
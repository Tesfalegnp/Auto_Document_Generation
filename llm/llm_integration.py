"""
Deep README generator from AST JSON.

- Parses full AST structure
- Extracts per-file: language, classes, functions, variables
- Sends rich summary to Gemini
- Outputs comprehensive, file-by-file README in Markdown
"""

import os
import json
import textwrap
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path="/home/hope/Project_package/galaxy-app/AI_document/.env")

try:
    from google import genai
except ImportError:
    raise ImportError("Please install: pip install google-genai")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)
DEFAULT_MODEL = "gemini-2.0-flash"


def _extract_entities(node: Dict[str, Any], indent: int = 0) -> List[str]:
    """Recursively extract classes, functions, vars from a file node."""
    lines = []
    prefix = "  " * indent

    node_type = node.get("type", "").lower()
    name = node.get("name") or node.get("path") or "unknown"

    if node_type == "file":
        lang = node.get("language", "unknown")
        lines.append(f"{prefix}📄 **File**: `{name}` | Language: `{lang}`")
        if "children" in node:
            for child in node["children"]:
                lines.extend(_extract_entities(child, indent + 1))
    elif node_type == "class":
        lines.append(f"{prefix}CppClass `{name}`")
        if "methods" in node:
            for method in node["methods"]:
                lines.append(f"{prefix}  - Method: `{method}`")
    elif node_type == "function":
        sig = node.get("signature", "")
        lines.append(f"{prefix}CppMethod `{name}{sig}`")
    elif node_type == "variable":
        value = node.get("value", "")
        lines.append(f"{prefix}CppMethod Variable: `{name}` = `{value}`"[:100])
    elif node_type == "module":
        lines.append(f"{prefix}📦 Module: `{name}`")
        if "children" in node:
            for child in node["children"]:
                lines.extend(_extract_entities(child, indent + 1))
    else:
        # Fallback: treat as generic node
        if "children" in node:
            lines.append(f"{prefix}📁 {name}")
            for child in node["children"]:
                lines.extend(_extract_entities(child, indent + 1))

    return lines


def summarize_json_for_readme(json_obj: Dict[str, Any]) -> str:
    """
    Generate a rich, structured summary of the entire codebase
    suitable for LLM to generate deep documentation.
    """
    if not isinstance(json_obj, dict):
        return "Invalid JSON structure."

    summary_lines = []
    summary_lines.append("# Project Code Structure Summary\n")

    # Walk the tree — assume root may have 'children' or be a file list
    nodes_to_process = []
    if "children" in json_obj:
        nodes_to_process = json_obj["children"]
    elif isinstance(json_obj.get("files"), list):
        nodes_to_process = json_obj["files"]
    elif isinstance(json_obj, dict) and json_obj.get("type") == "project":
        nodes_to_process = json_obj.get("children", [])
    else:
        # Fallback: treat top-level keys as files/modules
        nodes_to_process = [v for v in json_obj.values() if isinstance(v, dict) and "type" in v]

    for node in nodes_to_process:
        if isinstance(node, dict):
            entity_lines = _extract_entities(node)
            if entity_lines:
                summary_lines.extend(entity_lines)
                summary_lines.append("")  # blank line between files

    return "\n".join(summary_lines)


def build_prompt(json_summary: str) -> str:
    """Build a detailed prompt for deep README generation."""
    prompt = textwrap.dedent(f"""
        You are a world-class software documentation engineer.
        Your task: generate a **comprehensive, professional README.md** that explains the ENTIRE codebase
        so thoroughly that a developer can understand the system **without reading a single line of source code**.

        Use the structured project summary below. It contains:
        - Every file, its language, and purpose
        - All classes, functions, and key variables
        - Hierarchical relationships

        ## Requirements for the README:
        1. **Start with a clear title and 2-sentence overview** of the project's purpose.
        2. **Project Structure**: Explain the high-level architecture (e.g., parser → walker → output).
        3. **File-by-File Deep Dive**: For each file:
           - State its role in the system
           - List and explain key classes/functions
           - Mention language and notable patterns
        4. **Cross-File Relationships**: Explain how files/modules interact (e.g., "walker.py is used by generate_ast_docs.py to traverse the AST").
        5. **Getting Started**: Include exact CLI commands to run the AST generator and README generator.
        6. **Output Examples**: Mention generated files (ast_summary.json, etc.)
        7. **Style**: Use clear Markdown headers, bullet points, and fenced code blocks for commands.
        8. **Tone**: Professional, precise, and educational — assume the reader is technical but new to this codebase.

        ## Output Rules:
        - Return ONLY valid Markdown.
        - NO disclaimers, NO "based on the summary", NO extra commentary.
        - Begin immediately with `# Project Title`.

        --- BEGIN PROJECT SUMMARY ---
        {json_summary}
        --- END PROJECT SUMMARY ---
    """).strip()
    return prompt


def call_gemini(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Gemini with prompt."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text if hasattr(response, "text") else str(response)


def generate_from_json_file(json_path: str, model: str = DEFAULT_MODEL) -> str:
    """Load JSON, create rich summary, generate deep README."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_summary = summarize_json_for_readme(data)
    prompt = build_prompt(json_summary)
    return call_gemini(prompt, model=model)
# Title: {{Project Title}}

# Short description (1-2 lines):

# High-level Architecture:

# - Inputs: e.g. directory path -> AST JSON

# - Processing steps: walker -> parser_layer -> traversal_layer -> output_layer

# - Outputs: docs/ast_summary.json, docs/ast_graph.graphml, docs/ast_embeddings.json

# Installation:

# - pip install -r requirements.txt

# Quickstart:

# - python -m galaxy_ast_docs.generate_ast_docs --root /path/to/repo --output docs/ast_summary.json

# - python llm/generate_readme.py --json docs/ast_summary.json --out README_docs.md

# Example usage and CLI commands:

# - Show typical commands and expected outputs

# Notes:

# - Tell where to put the GEMINI_API_KEY (use .env)

# - Mention limitations (large JSON chunking)

# Next steps & enhancements:

# - Add CI to generate docs automatically

# - Add tests and more robust error handling
# Project Documentation

You are an expert software architect and technical writer. Generate a comprehensive, developer-friendly README in Markdown using the provided AST summary.

## Requirements

For **each notable source file** (especially .py, .js, .rs, .java, .metta, etc.), include:

- **File path**
- **General purpose**: What problem does this file solve? Why does it exist?
- **Key classes**: List class names and a 1-sentence role for each.
- **Key functions**: List top-level or exported functions and their purpose.
- **Important variables/constants**: If they control behavior, config, or state.
- **Dependencies/imports**: Only if they reveal architectural intent.

Also include:

- A **Project Overview** section explaining the system’s goal.
- A **Project Structure** tree (top-level dirs + 1-line descriptions).
- **How to reproduce**: Exact commands to regenerate this doc.
- **Assumptions**: What the parser inferred (e.g., “detected Python + MeTTa”).

## Style Rules

- Use clear headings (`## File: src/core/engine.py`)
- Use bullet points for lists
- Wrap code/commands in ```bash or ```python
- **Do not hallucinate** — only describe what’s in the AST summary.
- If a file has no functions/classes, skip deep analysis.
- Prioritize clarity over length.

## Output Format

Return ONLY valid Markdown. Start with `# Project Documentation`, no intro text.
# tools/md_to_html.py
"""
Convert README_docs.md to a beautiful, self-contained HTML page.
Run: python tools/md_to_html.py --md README_docs.md --out docs/index.html
"""

import argparse
import markdown
import re
from pathlib import Path

def add_anchors(html: str) -> str:
    """Add anchor links to headers (like GitHub)."""
    def replace_header(m):
        level = m.group(1)
        title = m.group(2)
        anchor = re.sub(r"[^a-zA-Z0-9\s]", "", title).replace(" ", "-").lower()
        return f'<h{level} id="{anchor}">{title} <a class="anchor" href="#{anchor}" aria-hidden="true">#</a></h{level}>'
    return re.sub(r'<h([1-6])>(.*?)</h\1>', replace_header, html)

def generate_html(md_content: str) -> str:
    # Convert Markdown to HTML with code highlighting
    html_body = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc'
        ]
    )
    html_body = add_anchors(html_body)

    # Inline CSS (modern, clean, dark-mode compatible)
    css = """
    <style>
    :root {
        --bg: #ffffff;
        --text: #24292e;
        --code-bg: #f6f8fa;
        --border: #d0d7de;
        --link: #0969da;
        --header-bg: #f6f8fa;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg: #0d1117;
            --text: #c9d1d9;
            --code-bg: #161b22;
            --border: #30363d;
            --link: #58a6ff;
            --header-bg: #161b22;
        }
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        line-height: 1.6;
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 1rem;
        background: var(--bg);
        color: var(--text);
    }
    h1, h2, h3, h4, h5, h6 {
        margin-top: 1.5em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid var(--border);
    }
    h1 {
        font-size: 2.2em;
        border: none;
        background: var(--header-bg);
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0;
    }
    a {
        color: var(--link);
        text-decoration: none;
    }
    a:hover { text-decoration: underline; }
    pre {
        background: var(--code-bg);
        border-radius: 6px;
        padding: 16px;
        overflow: auto;
        border: 1px solid var(--border);
    }
    code {
        background: var(--code-bg);
        padding: 0.2em 0.4em;
        border-radius: 6px;
        font-size: 85%;
    }
    pre code {
        padding: 0;
        background: none;
    }
    .anchor {
        opacity: 0;
        margin-left: 0.5em;
        text-decoration: none;
        color: var(--link);
    }
    h1:hover .anchor,
    h2:hover .anchor,
    h3:hover .anchor {
        opacity: 1;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }
    th, td {
        padding: 0.6em 1em;
        border: 1px solid var(--border);
    }
    th {
        background: var(--header-bg);
    }
    </style>
    """

    # Code highlighting CSS (Pygments-compatible)
    pygments_css = """
    <style>
    .codehilite .hll { background-color: #ffffcc }
    .codehilite .c { color: #6a737d; font-style: italic } /* Comment */
    .codehilite .err { color: #a61717; background-color: #e3d2d2 } /* Error */
    .codehilite .k { color: #d73a49; font-weight: bold } /* Keyword */
    .codehilite .o { color: #6f42c1; font-weight: bold } /* Operator */
    .codehilite .ch { color: #6a737d; font-style: italic } /* Comment.Hashbang */
    .codehilite .cm { color: #6a737d; font-style: italic } /* Comment.Multiline */
    .codehilite .cp { color: #6a737d; font-style: italic } /* Comment.Preproc */
    .codehilite .cpf { color: #6a737d; font-style: italic } /* Comment.PreprocFile */
    .codehilite .c1 { color: #6a737d; font-style: italic } /* Comment.Single */
    .codehilite .cs { color: #6a737d; font-style: italic } /* Comment.Special */
    .codehilite .gd { color: #b31d28; background-color: #ffeef0 } /* Generic.Deleted */
    .codehilite .ge { font-style: italic } /* Generic.Emph */
    .codehilite .gr { color: #b31d28 } /* Generic.Error */
    .codehilite .gh { color: #005cc5; font-weight: bold } /* Generic.Heading */
    .codehilite .gi { color: #22863a; background-color: #f0fff4 } /* Generic.Inserted */
    .codehilite .go { color: #6a737d } /* Generic.Output */
    .codehilite .gp { color: #6a737d; font-weight: bold } /* Generic.Prompt */
    .codehilite .gs { font-weight: bold } /* Generic.Strong */
    .codehilite .gu { color: #6f42c1; font-weight: bold } /* Generic.Subheading */
    .codehilite .gt { color: #b31d28 } /* Generic.Traceback */
    .codehilite .kc { color: #d73a49; font-weight: bold } /* Keyword.Constant */
    .codehilite .kd { color: #d73a49; font-weight: bold } /* Keyword.Declaration */
    .codehilite .kn { color: #d73a49; font-weight: bold } /* Keyword.Namespace */
    .codehilite .kp { color: #d73a49; font-weight: bold } /* Keyword.Pseudo */
    .codehilite .kr { color: #d73a49; font-weight: bold } /* Keyword.Reserved */
    .codehilite .kt { color: #d73a49; font-weight: bold } /* Keyword.Type */
    .codehilite .m { color: #005cc5 } /* Literal.Number */
    .codehilite .s { color: #032f62 } /* Literal.String */
    .codehilite .na { color: #6f42c1 } /* Name.Attribute */
    .codehilite .nb { color: #005cc5 } /* Name.Builtin */
    .codehilite .nc { color: #6f42c1; font-weight: bold } /* Name.Class */
    .codehilite .no { color: #005cc5 } /* Name.Constant */
    .codehilite .nd { color: #6f42c1 } /* Name.Decorator */
    .codehilite .ni { color: #6f42c1 } /* Name.Entity */
    .codehilite .ne { color: #6f42c1; font-weight: bold } /* Name.Exception */
    .codehilite .nf { color: #6f42c1; font-weight: bold } /* Name.Function */
    .codehilite .nl { color: #6f42c1 } /* Name.Label */
    .codehilite .nn { color: #6f42c1 } /* Name.Namespace */
    .codehilite .nt { color: #22863a } /* Name.Tag */
    .codehilite .nv { color: #e36209 } /* Name.Variable */
    .codehilite .ow { color: #d73a49; font-weight: bold } /* Operator.Word */
    .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
    .codehilite .mb { color: #005cc5 } /* Literal.Number.Bin */
    .codehilite .mf { color: #005cc5 } /* Literal.Number.Float */
    .codehilite .mh { color: #005cc5 } /* Literal.Number.Hex */
    .codehilite .mi { color: #005cc5 } /* Literal.Number.Integer */
    .codehilite .mo { color: #005cc5 } /* Literal.Number.Oct */
    .codehilite .sa { color: #032f62 } /* Literal.String.Affix */
    .codehilite .sb { color: #032f62 } /* Literal.String.Backtick */
    .codehilite .sc { color: #032f62 } /* Literal.String.Char */
    .codehilite .dl { color: #032f62 } /* Literal.String.Delimiter */
    .codehilite .sd { color: #032f62 } /* Literal.String.Doc */
    .codehilite .s2 { color: #032f62 } /* Literal.String.Double */
    .codehilite .se { color: #032f62 } /* Literal.String.Escape */
    .codehilite .sh { color: #032f62 } /* Literal.String.Heredoc */
    .codehilite .si { color: #032f62 } /* Literal.String.Interpol */
    .codehilite .sx { color: #032f62 } /* Literal.String.Other */
    .codehilite .sr { color: #032f62 } /* Literal.String.Regex */
    .codehilite .s1 { color: #032f62 } /* Literal.String.Single */
    .codehilite .ss { color: #032f62 } /* Literal.String.Symbol */
    .codehilite .bp { color: #005cc5 } /* Name.Builtin.Pseudo */
    .codehilite .fm { color: #6f42c1; font-weight: bold } /* Name.Function.Magic */
    .codehilite .vc { color: #e36209 } /* Name.Variable.Class */
    .codehilite .vg { color: #e36209 } /* Name.Variable.Global */
    .codehilite .vi { color: #e36209 } /* Name.Variable.Instance */
    .codehilite .vm { color: #e36209 } /* Name.Variable.Magic */
    .codehilite .il { color: #005cc5 } /* Literal.Number.Integer.Long */
    </style>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Documentation</title>
    {css}
    {pygments_css}
</head>
<body>
    {html_body}
</body>
</html>
    """
    return full_html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", default="README_docs.md", help="Input Markdown file")
    parser.add_argument("--out", default="docs/index.html", help="Output HTML file")
    args = parser.parse_args()

    md_path = Path(args.md)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = generate_html(md_text)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ Beautiful HTML docs generated: {out_path.resolve()}")
    print(f"👉 Open in browser: file://{out_path.resolve()}")


if __name__ == "__main__":
    main()
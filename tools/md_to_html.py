# tools/md_to_html.py
"""
Convert README_docs.md to an animated, interactive HTML page.
Features:
- Typing effect (typewriter style) for docs content
- Auto-scroll as content appears
- Spinner while loading
- Success popup when finished
- Sidebar Table of Contents (from Markdown headings)
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
    # Convert Markdown → HTML
    html_body = markdown.markdown(
        md_content,
        extensions=['fenced_code', 'codehilite', 'tables', 'toc']
    )
    html_body = add_anchors(html_body)

    # CSS + JS for animation, sidebar, toast
    css = """
    <style>
    body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        background: #0d1117;
        color: #c9d1d9;
        display: flex;
    }
    #sidebar {
        width: 250px;
        background: #161b22;
        padding: 1rem;
        height: 100vh;
        overflow-y: auto;
        position: fixed;
    }
    #sidebar h2 {
        font-size: 1.2em;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.5em;
        margin-top: 0;
    }
    #toc a {
        display: block;
        color: #58a6ff;
        text-decoration: none;
        margin: 0.3em 0;
        font-size: 0.9em;
    }
    #toc a:hover { text-decoration: underline; }
    #content-wrapper {
        margin-left: 270px;
        padding: 2rem;
        flex: 1;
        overflow-y: auto;
        height: 100vh;
    }
    #spinner {
        font-size: 1.5em;
        margin: 2rem auto;
        text-align: center;
        color: #58a6ff;
    }
    #success-toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #238636;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        display: none;
        font-weight: bold;
    }
    h1, h2, h3, h4, h5 {
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.3em;
    }
    pre {
        background: #161b22;
        padding: 1em;
        border-radius: 6px;
        overflow-x: auto;
    }
    code {
        background: #161b22;
        padding: 0.2em 0.4em;
        border-radius: 4px;
    }
    </style>
    """

    js = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const contentWrapper = document.getElementById("content");
        const spinner = document.getElementById("spinner");
        const toast = document.getElementById("success-toast");

        const fullHtml = `{html_body.replace("`", "\\`")}`;
        let idx = 0;
        spinner.style.display = "block";

        function typeChar() {{
            if (idx === 0) {{
                spinner.style.display = "none";
            }}
            if (idx < fullHtml.length) {{
                contentWrapper.innerHTML = fullHtml.slice(0, idx + 1);
                idx++;
                window.scrollTo(0, document.body.scrollHeight);
                setTimeout(typeChar, 10); // typing speed
            }} else {{
                toast.style.display = "block";
                setTimeout(() => toast.style.display = "none", 3000);
                buildTOC();
            }}
        }}

        function buildTOC() {{
            const toc = document.getElementById("toc");
            toc.innerHTML = "";
            const headers = contentWrapper.querySelectorAll("h1, h2, h3");
            headers.forEach(h => {{
                const link = document.createElement("a");
                link.href = "#" + h.id;
                link.textContent = h.textContent;
                toc.appendChild(link);
            }});
        }}

        typeChar();
    }});
    </script>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Project Documentation</title>
  {css}
</head>
<body>
  <div id="sidebar">
    <h2>📑 Table of Contents</h2>
    <div id="toc"></div>
  </div>
  <div id="content-wrapper">
    <div id="spinner">⏳ Loading...</div>
    <div id="content"></div>
  </div>
  <div id="success-toast">✅ Documentation Loaded Successfully!</div>
  {js}
</body>
</html>"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", default="README_docs.md", help="Input Markdown file")
    parser.add_argument("--out", default="docs/index.html", help="Output HTML file")
    args = parser.parse_args()

    md_path = Path(args.md)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    html = generate_html(md_text)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"✅ Animated HTML docs generated: {out_path.resolve()}")
    print(f"👉 Open in browser: file://{out_path.resolve()}")

if __name__ == "__main__":
    main()

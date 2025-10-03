# Auto Document Generation 🚀

> AI-powered auto document creator for any project

Auto Document Generation is a tool that automates the creation of rich project documentation (README, AST summaries, HTML docs, etc.) for any codebase by combining AST parsing and LLM-powered content generation. It reduces manual effort and ensures your docs stay up-to-date with your code.

## Table of Contents

- [Features](#features)  
- [Demo / Screenshots](#demo--screenshots)  
- [Installation](#installation)  
- [Usage](#usage)  
- [How It Works](#how-it-works)  
- [Project Structure](#project-structure)  
- [Configuration / Options](#configuration--options)  
- [Contributing](#contributing)  
- [License](#license)  
- [Acknowledgments](#acknowledgments)

## Features

- 📄 Generates an AST summary of your project  
- 🤖 Uses LLM to produce a high-quality README from AST  
- 📝 Converts Markdown to HTML to create browsable documentation  
- 🧰 All steps can be run with a single command  
- Extendable parsers for multiple languages  
- Suitable for integrating into CI/CD pipelines  


## Demo 🎥

<video src="demo.webm" autoplay loop muted playsinline width="600">
  Your browser does not support the video tag.
</video>


## Installation

Clone the repository:

```bash
git clone https://github.com/Tesfalegnp/Auto_Document_Generation.git
cd Auto_Document_Generation
````

Set up a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ Make sure your dependencies include any library your LLM wrapper or parser modules require (e.g. OpenAI SDK, ast parsing libs, markdown converters, etc.)

## Usage

Once installed, you can generate documentation for any project by running:

```bash
python run_docs.py --root /path/to/your/project
```

This command will sequentially:

1. Build language parsers (if needed)
2. Parse the target project into AST JSON
3. Generate a README via LLM
4. Convert the generated README to HTML and open it

If you already built parsers and wish to skip that step:

```bash
python run_docs.py --root /path/to/your/project --skip-build
```

To prevent automatically opening the HTML in a browser (useful in headless environments):

```bash
python run_docs.py --root /path/to/your/project --no-open
```

### Example

```bash
python run_docs.py --root ~/Projects/MyApp
```

This will generate:

* `docs/ast_summary.json`
* `README_docs.md`
* `docs/index.html` (viewable in your browser)

## How It Works

1. **AST Extraction**
   Your target code is parsed into an AST, producing structured JSON that captures modules, functions, classes, docstrings, and code relationships.

2. **LLM-Driven Content Generation**
   The AST JSON is fed into a prompt pipeline, producing high-level documentation like usage instructions, architecture overviews, and module summaries.

3. **Markdown to HTML**
   The generated README Markdown is converted into HTML for pretty viewing, and optionally opened in your browser.

4. **Modular Architecture**
   Each step lives in its own module (`galaxy_ast_docs`, `llm`, `tools`) and can be extended or replaced.

## Project Structure

```text
Auto_Document_Generation/
├── galaxy_ast_docs/
├── llm/
├── tools/
├── run_docs.py
├── requirements.txt
├── README.md          ← this file
└── docs/              ← output folder (auto-created)
```

## Configuration / Options

You can pass optional flags to `run_docs.py`:

| Flag           | Description                                 |
| -------------- | ------------------------------------------- |
| `--root`       | (Required) Path to project to document      |
| `--skip-build` | Skip rebuilding of parsers                  |
| `--no-open`    | Don’t open the generated HTML automatically |

Internally, modules may support additional flags (e.g. `--output`, `--json`, etc.). You can view help by running:

```bash
python -m galaxy_ast_docs.generate_ast_docs --help
python -m llm.generate_readme --help
python -m tools.md_to_html --help
```

## Contributing

Contributions are welcome! Here are some ways you can help:

* Add support for more programming languages
* Improve prompt templates or LLM pipelines
* Add CI integration (e.g. auto-docs on PR commit)
* Write tests for each step
* Improve styling of the HTML output

To contribute:

1. Fork the repo
2. Create a branch (`git checkout -b feat/your-feature`)
3. Implement and test
4. Submit a Pull Request

Please follow the repository’s coding style and include documentation for any new features.

## License

*(Replace with your chosen license, e.g. MIT, Apache 2.0, etc.)*

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

* Based on AST parsing + LLM synergy
* Inspiration from other auto-documentation tools and open-source projects
* Thanks to the community for feedback and ideas

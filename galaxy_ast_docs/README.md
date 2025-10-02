# Galaxy AST Documentation Tool with Tree-sitter

Generates structured code documentation using Abstract Syntax Tree (AST) parsing. Extracts classes, functions, and variables from source code with line numbers for easy navigation.

## Features
- Supports Python, JavaScript, and Java 
- Extracts classes, functions, and variables with line numbers
- Ignores binary/non-code files
- Handles large codebases efficiently
- Generates JSON documentation for easy processing
- Debug mode for troubleshooting

## Prerequisites
- Python 3.8+
- Build tools:
  ```bash
  # Ubuntu/Debian
  sudo apt install build-essential python3-dev
  
  # macOS
  xcode-select --install
  ```

## Setup
1. **Install Python dependencies:**
   ```bash
   pip install tree_sitter==0.22.1
   ```

2. **Clone parser repositories:**
   ```bash
   cd galaxy_ast_docs/parsers
   git clone https://github.com/tree-sitter/tree-sitter-python
   git clone https://github.com/tree-sitter/tree-sitter-javascript
   git clone https://github.com/tree-sitter/tree-sitter-java
   ```

3. **Build language bindings:**
   ```bash
   python -m galaxy_ast_docs.build_parsers
   ```
   Successful build output:
   ```
   === Building Tree-sitter languages ===
   Building library: /path/to/galaxy_ast_docs/build/my-languages.so
   ✅ Build complete: /path/to/galaxy_ast_docs/build/my-languages.so
   ```

## Usage
Generate documentation for your project:
```bash
python -m galaxy_ast_docs.generate_ast_docs \
    --root galaxy_app \
    --output galaxy_ast_docs/ast_documentation.json
```

### Advanced Options
| Option | Description | Default |
|--------|-------------|---------|
| `--root` | Source directory to scan | `.` (current dir) |
| `--output` | Output JSON file path | `ast_documentation.json` |
| `--debug` | Enable verbose debug logging | Disabled |

### Example Output
```json
[
  {
    "file": "galaxy_app/main.py",
    "language": "python",
    "definitions": [
      {
        "type": "class",
        "name": "GalaxyServer",
        "line": 15
      },
      {
        "type": "function",
        "name": "start_server",
        "line": 32
      },
      {
        "type": "variable",
        "name": "config",
        "line": 45
      }
    ]
  }
]
```

## Output Interpretation
- `file`: Relative path to source file
- `language`: Detected programming language
- `definitions`: List of extracted code elements
  - `type`: `class`, `function`, or `variable`
  - `name`: Name of the element
  - `line`: Line number in source file

## Adding New Languages
1. Clone the language parser:
   ```bash
   cd galaxy_ast_docs/parsers
   git clone https://github.com/tree-sitter/tree-sitter-<language>
   ```

2. Update `language_layer.py`:
   ```python
   # Add to EXT_MAP
   EXT_MAP = {
       ...
       ".ext": "newlang"
   }
   
   # Add to PARSERS
   PARSERS = {
       ...
       "newlang": "tree-sitter-newlang"
   }
   ```

3. Update `traversal_layer.py` with extraction rules for the new language

4. Rebuild parsers:
   ```bash
   python -m galaxy_ast_docs.build_parsers
   ```

## Troubleshooting

### Build Errors
```bash
AttributeError: type object 'tree_sitter.Language' has no attribute 'build_library'
```
**Solution:**
```bash
pip uninstall -y tree_sitter
pip install --no-cache-dir tree_sitter
```

### Parser Version Issues
```bash
Incompatible Language version 14. Must be between 13 and 13
```
**Solution:**
1. Update parsers:
   ```bash
   cd galaxy_ast_docs/parsers
   for dir in tree-sitter-*; do git -C $dir pull; done
   cd ../..
   python -m galaxy_ast_docs.build_parsers
   ```
   
2. Or reset to specific version:
   ```bash
   cd galaxy_ast_docs/parsers/tree-sitter-python
   git checkout v0.20.0
   ```

### No Definitions Found
1. Verify file has supported extension
2. Check debug output for processing messages
3. Ensure code contains class/function definitions

### Debugging
Run with debug mode to see detailed processing:
```bash
python -m galaxy_ast_docs.generate_ast_docs \
    --root galaxy_app \
    --output debug_output.json \
    --debug
```

Sample debug output:
```
🔍 Scanning codebase at: /path/to/galaxy_app
🌐 Supported languages: python, javascript, java
DEBUG:root:Processed galaxy_app/main.py - 23 definitions found
DEBUG:root:Skipping unsupported file: galaxy_app/config.ini
📊 Processed 5 files, 0 errors
✅ Documentation generated: debug_output.json
```

## Sample Workflow in my case
```bash
# you can Navigate to your project root
cd ~/Project_package/galaxy-app

# Build parsers
python -m Docs_generator.build_parsers

# Generate documentation
python -m Docs_generator.generate_ast_docs \
    --root galaxy_app \
    --output docs/ast_summary.json
    
# View results
jq '.' docs/ast_summary.json | less
```

## License
MIT License - Free for personal and commercial use
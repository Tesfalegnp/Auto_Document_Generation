# galaxy_ast_docs/output_layer.py
import json
import os

def save_to_json(data, output_file="ast_documentation.json"):
    dir_name = os.path.dirname(output_file)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Documentation generated: {output_file}")

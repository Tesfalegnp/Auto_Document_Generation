# galaxy_ast_docs/generate_ast_docs.py
import os
import argparse
import json
import networkx as nx
from node2vec import Node2Vec

from .walker import walk_and_parse
from .output_layer import save_to_json
from .language_layer import available_languages

def main():
    """Main entry point for AST documentation, graph, and embeddings generation"""
    parser = argparse.ArgumentParser(description='Generate AST documentation, Knowledge Graph, and Embeddings')
    parser.add_argument('--root', default='.', help='Root directory to scan')
    parser.add_argument('--output', default='docs/ast_summary.json', help='Output JSON file path')
    parser.add_argument('--graph-output', default='docs/ast_graph.graphml', help='Graph output file path (.graphml)')
    parser.add_argument('--emb-output', default='docs/ast_embeddings.json', help='Embeddings output file path')
    parser.add_argument('--debug', action='store_true', help='Enable verbose debug output')
    parser.add_argument('--metta-only', action='store_true', help='Only process MeTTa files')
    args = parser.parse_args()

    print(f"🔍 Scanning: {os.path.abspath(args.root)}")
    print(f"🌐 Languages supported: {', '.join(available_languages())}")
    
    if args.metta_only:
        print("🎯 MeTTa-only mode enabled")

    # === Step 1: Tree (JSON) ===
    results = walk_and_parse(args.root, debug=args.debug)
    
    if args.metta_only:
        results = filter_metta_only(results)

    save_to_json(results, args.output)
    print_summary(results)

    # === Step 2: Tree → Graph ===
    G = build_graph_from_tree(results)
    nx.write_graphml(G, args.graph_output)
    print(f"✅ Graph saved to: {args.graph_output}")

    # === Step 3: Graph → Embeddings ===
    if len(G.nodes) > 0:
        node2vec = Node2Vec(G, dimensions=64, walk_length=20, num_walks=100, workers=1)
        model = node2vec.fit(window=10, min_count=1, batch_words=4)

        embeddings = {str(node): model.wv[str(node)].tolist() for node in G.nodes()}
        with open(args.emb_output, "w", encoding="utf-8") as f:
            json.dump(embeddings, f, indent=2)
        print(f"✅ Embeddings saved to: {args.emb_output}")
    else:
        print("⚠️ Graph empty — skipping embeddings")

def filter_metta_only(tree_data):
    """Filter tree to only include MeTTa files"""
    if tree_data["type"] == "file":
        if tree_data.get("language") == "metta":
            return tree_data
        else:
            return None
    elif tree_data["type"] == "folder":
        filtered_children = []
        for child in tree_data.get("children", []):
            filtered_child = filter_metta_only(child)
            if filtered_child:
                filtered_children.append(filtered_child)
        
        if filtered_children:
            tree_data["children"] = filtered_children
            return tree_data
        else:
            return None
    
    return tree_data

def print_summary(tree_data):
    """Print summary of parsed files"""
    stats = {"total_files": 0, "metta_files": 0, "other_files": 0, "errors": 0}
    
    def count_files(node):
        if node["type"] == "file":
            stats["total_files"] += 1
            if node.get("language") == "metta":
                stats["metta_files"] += 1
            else:
                stats["other_files"] += 1
            if "parse_error" in node:
                stats["errors"] += 1
        elif node["type"] == "folder":
            for child in node.get("children", []):
                count_files(child)
    
    count_files(tree_data)
    
    print(f"\n📊 Summary:")
    print(f"   Total files: {stats['total_files']}")
    print(f"   MeTTa files: {stats['metta_files']}")
    print(f"   Other files: {stats['other_files']}")
    print(f"   Parse errors: {stats['errors']}")

def build_graph_from_tree(tree_data):
    """Convert parsed AST tree into a graph"""
    G = nx.DiGraph()

    def add_node(node, parent=None):
        node_id = node.get("path", node.get("name"))
        G.add_node(node_id, type=node["type"], name=node["name"])

        if parent:
            G.add_edge(parent, node_id, relation="contains")

        # For files: add definitions
        if node["type"] == "file" and "definitions" in node:
            defs = node["definitions"]

            for cls in defs.get("classes", []):
                class_id = f"{node_id}:{cls['name']}"
                G.add_node(class_id, type="class", name=cls["name"])
                G.add_edge(node_id, class_id, relation="defines")

                for func in cls.get("functions", []):
                    func_id = f"{class_id}:{func['name']}"
                    G.add_node(func_id, type="function", name=func["name"])
                    G.add_edge(class_id, func_id, relation="hasMethod")

            for func in defs.get("functions", []):
                func_id = f"{node_id}:{func['name']}"
                G.add_node(func_id, type="function", name=func["name"])
                G.add_edge(node_id, func_id, relation="defines")

        # Recurse
        for child in node.get("children", []):
            add_node(child, node_id)

    add_node(tree_data, None)
    return G

if __name__ == "__main__":
    main()
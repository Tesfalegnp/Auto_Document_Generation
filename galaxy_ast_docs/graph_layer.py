# galaxy_ast_docs/graph_layer.py
import networkx as nx
import json
from pathlib import Path

def json_to_graph(json_file, output_graphml="ast_graph.graphml", output_ttl=None):
    """
    Convert the hierarchical JSON tree into a Knowledge Graph using NetworkX.
    Nodes = files, classes, functions, variables
    Edges = contains, defines, uses
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    def add_node_recursive(node, parent=None):
        node_id = node["path"] if "path" in node else node["name"]

        # Add node with attributes
        G.add_node(node_id, **{
            "name": node["name"],
            "type": node["type"],
            "language": node.get("language", ""),
        })

        # Add parent-child edge
        if parent:
            G.add_edge(parent, node_id, relation="contains")

        # Handle definitions inside files
        if node["type"] == "file" and "definitions" in node:
            defs = node["definitions"]

            # Classes
            for cls in defs.get("classes", []):
                class_id = f"{node_id}::class::{cls['name']}"
                G.add_node(class_id, type="class", name=cls["name"])
                G.add_edge(node_id, class_id, relation="defines")

                # Functions inside class
                for func in cls.get("functions", []):
                    func_id = f"{class_id}::func::{func['name']}"
                    G.add_node(func_id, type="function", name=func["name"])
                    G.add_edge(class_id, func_id, relation="defines")

                    # Variables inside function
                    for var in func.get("variables", []):
                        var_id = f"{func_id}::var::{var}"
                        G.add_node(var_id, type="variable", name=var)
                        G.add_edge(func_id, var_id, relation="uses")

            # Functions outside classes
            for func in defs.get("functions", []):
                func_id = f"{node_id}::func::{func['name']}"
                G.add_node(func_id, type="function", name=func["name"])
                G.add_edge(node_id, func_id, relation="defines")

                for var in func.get("variables", []):
                    var_id = f"{func_id}::var::{var}"
                    G.add_node(var_id, type="variable", name=var)
                    G.add_edge(func_id, var_id, relation="uses")

        # Recurse children
        for child in node.get("children", []):
            add_node_recursive(child, node_id)

    # Start recursion
    add_node_recursive(data)

    # Save graph
    Path(output_graphml).parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, output_graphml)
    print(f"✅ Graph saved: {output_graphml}")

    if output_ttl:
        try:
            import rdflib
            g = rdflib.Graph()
            for u, v, attrs in G.edges(data=True):
                g.add((rdflib.URIRef(u), rdflib.URIRef(attrs["relation"]), rdflib.URIRef(v)))
            g.serialize(output_ttl, format="turtle")
            print(f"✅ RDF Turtle saved: {output_ttl}")
        except ImportError:
            print("⚠️ Install rdflib to export RDF Turtle")

    return G

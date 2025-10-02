# galaxy_ast_docs/embedding_layer.py
import networkx as nx
from gensim.models import Word2Vec
from networkx.readwrite import json_graph
import random

def graph_to_embeddings(G, dimensions=64, walk_length=10, num_walks=20, window_size=5, workers=2, output_model="graph2vec.model"):
    """
    Learn node embeddings using Node2Vec-style random walks + Word2Vec
    """
    walks = []

    nodes = list(G.nodes())
    for _ in range(num_walks):
        random.shuffle(nodes)
        for node in nodes:
            walk = [node]
            current = node
            for _ in range(walk_length - 1):
                neighbors = list(G.neighbors(current))
                if not neighbors:
                    break
                current = random.choice(neighbors)
                walk.append(current)
            walks.append(walk)

    # Train Word2Vec on walks
    model = Word2Vec(
        sentences=walks,
        vector_size=dimensions,
        window=window_size,
        min_count=0,
        sg=1,
        workers=workers
    )

    model.save(output_model)
    print(f"✅ Embedding model saved: {output_model}")

    # Return dictionary {node_id: embedding}
    embeddings = {node: model.wv[node] for node in G.nodes() if node in model.wv}
    return embeddings

import networkx as nx


def simplify_graph(graph,
                   min_activity_significance=0.15,
                   min_path_importance=0.10):

    G = graph.copy()

    # -------- REMOVE WEAK ACTIVITIES --------

    for node, data in list(G.nodes(data=True)):

        sig = data.get("significance", 1)

        if sig < min_activity_significance:

            G.remove_node(node)

    # -------- REMOVE WEAK PATHS --------

    for u, v, data in list(G.edges(data=True)):

        imp = data.get("importance", 1)

        if imp < min_path_importance:

            G.remove_edge(u, v)

    # -------- REMOVE ISOLATED --------

    isolated = list(nx.isolates(G))

    G.remove_nodes_from(isolated)

    return G
import networkx as nx


def add_gdpr_overlay(base_graph, annotation_model):

    G = base_graph.copy()

    if annotation_model is None:
        return G

    for node in list(base_graph.nodes):

        annotations = annotation_model.get_annotations(node)

        for i, ann in enumerate(annotations):

            event = ann["event"]

            gdpr_node = f"{event.name}__{node}__{i}"

            G.add_node(
                gdpr_node,
                is_gdpr=True,
                size=60,
                importance=0.3
            )

            # conexión visual ligera
            G.add_edge(node, gdpr_node, weight=0.1)
            G.add_edge(gdpr_node, node, weight=0.1)

    return G
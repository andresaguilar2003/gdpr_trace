import networkx as nx
import math
from collections import defaultdict

START = "START"
END = "END"


# ============================================================
# MAIN PATH DETECTION (strongest flow path)
# ============================================================

def compute_main_path(graph):

    path = []
    node = START
    visited = set()

    while True:

        edges = list(graph.out_edges(node, data=True))

        if not edges:
            break

        total = sum(d.get("weight", 1) for _, _, d in edges)

        # penaliza loops y nodos débiles
        def score(e):
            _, v, d = e
            w = d.get("weight", 1)
            penalty = 0.5 if v in visited else 1.0
            return (w / total) * penalty

        best = max(edges, key=score)

        _, nxt, _ = best

        if nxt in visited:
            break

        path.append((node, nxt))
        visited.add(node)

        node = nxt

        if node == END:
            break

    main_nodes = {START}
    for _, v in path:
        main_nodes.add(v)

    return path, main_nodes


def compute_global_order(graph):

    importance = compute_node_importance(graph)

    return sorted(
        graph.nodes,
        key=lambda n: importance.get(n, 0),
        reverse=True
    )

def compute_depth(graph):

    depth = {START: 0}

    queue = [START]

    while queue:

        u = queue.pop(0)

        for _, v in graph.out_edges(u):

            new_depth = depth[u] + 1

            if v not in depth or new_depth > depth[v]:
                depth[v] = new_depth
                queue.append(v)

    return depth

# ============================================================
# NODE IMPORTANCE
# ============================================================

def compute_node_importance(graph):

    freq = {}

    for n in graph.nodes:

        incoming = sum(
            d.get("weight", 1)
            for _, _, d in graph.in_edges(n, data=True)
        )

        outgoing = sum(
            d.get("weight", 1)
            for _, _, d in graph.out_edges(n, data=True)
        )

        freq[n] = incoming + outgoing

    if not freq:
        return {}

    max_freq = max(freq.values())

    return {
        n: freq[n] / max_freq
        for n in freq
    }


# ============================================================
# NODE RANK (used for ordering)
# ============================================================

def compute_node_rank(graph):

    rank = {}

    for n in graph.nodes:

        incoming = sum(
            d.get("weight", 1)
            for _, _, d in graph.in_edges(n, data=True)
        )

        outgoing = sum(
            d.get("weight", 1)
            for _, _, d in graph.out_edges(n, data=True)
        )

        rank[n] = incoming + outgoing

    return rank


# ============================================================
# VARIANT TUBES
# ============================================================

def compute_variant_tubes(graph, main_nodes):

    tubes = defaultdict(list)

    for u, v in graph.edges():

        if u in main_nodes and v not in main_nodes:
            tubes[u].append(v)

    return tubes


# ============================================================
# CROSSING MINIMIZATION
# ============================================================

def minimize_crossings(nodes, graph):

    score = {}

    for n in nodes:

        score[n] = sum(
            data.get("weight", 1)
            for _, _, data in graph.out_edges(n, data=True)
        )

    return sorted(nodes, key=lambda x: score.get(x, 0), reverse=True)


# ============================================================
# DYNAMIC SPACING
# ============================================================

def compute_dynamic_spacing(graph):

    n = len(graph.nodes)

    if n < 20:
        return 240
    elif n < 40:
        return 280
    elif n < 80:
        return 320
    elif n < 150:
        return 360
    else:
        return 420


# ============================================================
# DISCO STYLE LAYOUT (PRO VERSION)
# ============================================================

def disco_layout(graph):
    # 🔥 FILTRAR grafo base (sin GDPR)
    base_graph = nx.DiGraph()

    for u, v, d in graph.edges(data=True):
        if graph.nodes[u].get("artificial") or graph.nodes[v].get("artificial"):
            continue
        base_graph.add_edge(u, v, **d)

    for n, d in graph.nodes(data=True):
        if not d.get("artificial"):
            base_graph.add_node(n, **d)

    spacing_y = compute_dynamic_spacing(graph)
    spacing_x = 240

    pos = {}

    main_path, main_nodes = compute_main_path(base_graph)
    importance = compute_node_importance(base_graph)

    # -------------------------------
    # 1. MAIN PATH (NO perfectamente recto)
    # -------------------------------

    y = 0
    pos[START] = (0, y)

    ordered_main = [v for _, v in main_path if v != END]

    for i, node in enumerate(ordered_main):

        y = (i + 1) * spacing_y

        # ligera desviación tipo DISCO
        x_offset = ((i % 2) * 2 - 1) * 20

        pos[node] = (x_offset, y)

    # -------------------------------
    # 2. VARIANTES AGRUPADAS (MEJORADO)
    # -------------------------------

    tubes = compute_variant_tubes(graph, main_nodes)

    side_offset = spacing_x
    tube_spacing = 100

    MAX_VARIANTS = 6

    for main_node, nodes in tubes.items():

        nodes = sorted(
            nodes,
            key=lambda n: importance.get(n, 0),
            reverse=True
        )[:MAX_VARIANTS]

        if main_node not in pos:
            continue

        base_x, base_y = pos[main_node]

        # ORDEN GLOBAL (no local)
        nodes = sorted(
            nodes,
            key=lambda n: importance.get(n, 0),
            reverse=True
        )

        left_y = base_y
        right_y = base_y

        for i, n in enumerate(nodes):

            if n in pos:
                continue

            if i % 2 == 0:
                left_y += tube_spacing
                pos[n] = (base_x - side_offset, left_y)
            else:
                right_y += tube_spacing
                pos[n] = (base_x + side_offset, right_y)

    # -------------------------------
    # 3. COLOCACIÓN INTELIGENTE RESTANTE
    # -------------------------------

    remaining = [n for n in graph.nodes if n not in pos]

    base_y = max(y for _, y in pos.values())

    ordered_remaining = sorted(
        remaining,
        key=lambda n: importance.get(n, 0),
        reverse=True
    )

    for i, n in enumerate(ordered_remaining):

        col = i % 6
        row = i // 6

        pos[n] = (
            (col - 2.5) * spacing_x * 0.8,
            base_y + spacing_y * (1 + row)
        )

    # -------------------------------
    # 4. COLOCAR END EL ÚLTIMO SIEMPRE
    # -------------------------------

    max_y = max(y for _, y in pos.values())

    pos[END] = (0, max_y + spacing_y)

    return pos

# ============================================================
# TRUE EDGE BUNDLING
# ============================================================

def compute_edge_bundle(u_pos, v_pos, index=0, total=1):

    x1, y1 = u_pos
    x2, y2 = v_pos

    dy = y2 - y1

    spread = 25
    offset = (index - total / 2) * spread

    mid_y = y1 + dy * 0.5

    ctrl1 = (x1, mid_y + offset)
    ctrl2 = (x2, mid_y + offset)

    return ctrl1, ctrl2


def filter_weak_edges(graph, threshold=0.05):

    to_remove = []

    for u, v, d in graph.edges(data=True):

        total = sum(
            data.get("weight", 1)
            for _, _, data in graph.out_edges(u, data=True)
        )

        if total == 0:
            continue

        prob = d.get("weight", 1) / total

        if prob < threshold:
            to_remove.append((u, v))

    graph.remove_edges_from(to_remove)


# ============================================================
# EDGE FLOW COMPRESSION
# ============================================================

def compute_flow_groups(graph):

    """
    Agrupa edges por nodo origen para crear bundles visuales.
    """

    groups = {}

    for u, v, data in graph.edges(data=True):

        groups.setdefault(u, []).append((u, v, data))

    return groups
import networkx as nx
import math

from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as start_activities
from pm4py.statistics.end_activities.log import get as end_activities
from pm4py.statistics.attributes.log import get as attributes_get

START = "START"
END = "END"

def is_case_special(name):
    return name in ["CASE_START", "CASE_END"]

def build_graph(
    log,
    min_node_freq=5,
    min_edge_weight=3,
    min_edge_prob=0.05,
    include_log_gdpr=True,
    include_case_gdpr=False,
    context=None
):
    # 🌟 CRÍTICO: Forzamos el descubrimiento mediante 'concept:name' para mantener el 
    # secuenciamiento real del flujo y evitar que colapse en megabloques como DATA_COLLECTION
    key = "concept:name"

    dfg = dfg_discovery.apply(log, parameters={
        "activity_key": key
    })

    start = start_activities.get_start_activities(log, parameters={
        "activity_key": key
    })

    end = end_activities.get_end_activities(log, parameters={
        "activity_key": key
    })

    activity_freq = attributes_get.get_attribute_values(
        log,
        key
    )

    # Mapeo auxiliar para extraer el tipo de actividad (graph:activity o gdpr:activity_type) de cada evento
    activity_type_mapping = {}
    try:
        for trace in log:
            for event in trace:
                c_name = event.get("concept:name")
                # Buscamos si tiene el tag de mapeo de datos o cumplimiento
                g_act = event.get("graph:activity") or event.get("gdpr:activity_type")
                if c_name and g_act:
                    # Guardamos la relación (Evitamos guardar si es redundante al nombre)
                    if g_act != c_name:
                        activity_type_mapping[c_name] = g_act
    except Exception as e:
        print(f"Error extrayendo metadatos de tipos de actividad: {e}")

    G = nx.DiGraph()

    # ---------- NODES ----------
    FIXED_NODE_SIZE = 120
    FIXED_FONT_SIZE = 11
    
    COLOR_GDPR = "#FFD700"      # Dorado
    COLOR_DEFAULT = "#3164a6"   # Azul
    COLOR_START_END = "#00c853" # Verde
    
    GDPR_KEYWORDS = [
        "verify_legal_basis", "check_consent", "privacy_notice_disclosed",
        "access_control_check", "minimisation_check", "encryption_applied",
        "check_third_party_agreement", "verify_international_safeguard",
        "automated_logic_disclosure", "retention_period_verify", "confirm_data_erasure",
        "record_purpose", "log_processing_activity"
    ]

    def is_gdpr_event(name):
        return any(k in name.lower() for k in GDPR_KEYWORDS)

    for node, count in activity_freq.items():
        if is_case_special(node):
            continue
        if not include_log_gdpr and is_gdpr_event(node):
            continue
        if count < min_node_freq:
            continue

        is_gdpr = is_gdpr_event(node)
        node_color = COLOR_GDPR if is_gdpr else COLOR_DEFAULT
        text_color = "black" if is_gdpr else "white"

        # 🌟 CONSTRUCCIÓN DEL NOMBRE COMBINADO EN EL MISMO BLOQUE
        # Si el nombre es 'ER Registration' y su tipo es 'DATA_COLLECTION', saldrá: "ER Registration\n[DATA_COLLECTION]"
        display_name = node
        activity_type = activity_type_mapping.get(node)
        if activity_type and activity_type != "GDPR_COMPLIANCE":
            display_name = f"{node}\n[{activity_type}]"

        G.add_node(
            node,
            label=display_name, # Mantenemos id interno limpio pero pasamos label compuesto
            frequency=count,
            size=FIXED_NODE_SIZE,
            font_size=FIXED_FONT_SIZE,
            fillcolor=node_color,
            color=node_color,
            fontcolor=text_color,
            style="filled"
        )

    # Coloreamos START y END de verde
    G.add_node(START, label=START, size=120, font_size=14, fillcolor=COLOR_START_END, color=COLOR_START_END, style="filled", fontcolor="white")
    G.add_node(END, label=END, size=120, font_size=14, fillcolor=COLOR_START_END, color=COLOR_START_END, style="filled", fontcolor="white")

    G.nodes[START]["rank"] = "source"
    G.nodes[END]["rank"] = "sink"

    # ---------- EDGES ----------
    MAX_EDGES_PER_NODE = 2
    outgoing = {}

    for (a, b), count in dfg.items():
        if a == "CASE_START":
            a = START
        if b == "CASE_END":
            b = END

        if a == "CASE_END" or b == "CASE_START":
            continue

        if a not in G.nodes or b not in G.nodes:
            continue

        if count < min_edge_weight:
            continue

        outgoing.setdefault(a, []).append((b, count))

    for a, edges in outgoing.items():
        total = activity_freq.get(a, 1)
        activity_freq[START] = activity_freq.get("CASE_START", 0)
        activity_freq[END] = activity_freq.get("CASE_END", 0)

        edges.sort(key=lambda x: x[1], reverse=True)
        best_count = edges[0][1]
        filtered_edges = []

        for i, (b, count) in enumerate(edges):
            prob = count / total
            relative = count / best_count
            dominance = best_count / total

            if i == 0:
                filtered_edges.append((b, count))
                continue

            if dominance > 0.85:
                continue
            if relative < 0.10:
                continue

            if total > 100:
                if relative < 0.20 or prob < 0.12:
                    continue
            elif total > 30:
                if relative < 0.25 or prob < 0.10:
                    continue

            filtered_edges.append((b, count))

        for b, count in filtered_edges[:MAX_EDGES_PER_NODE]:
            width = 1.5 + math.log(count + 1)
            G.add_edge(
                a,
                b,
                weight=count,
                width=width
            )
    
    if not include_case_gdpr:
        G = connect_start_end(G, start, end, activity_freq)
    else:
        G = connect_start_end(G, start, end, activity_freq)
        G = inject_case_gdpr_layer(G, context)

    return G

from app.specifications.activity_gdpr_mapping import ACTIVITY_GDPR_PATTERNS
from app.specifications.activity_types import ActivityType


def inject_case_gdpr_layer(G, context):

    # =====================================================
    # 0. OBTENER REGLAS DINÁMICAS
    # =====================================================

    start_rules = ACTIVITY_GDPR_PATTERNS.get(ActivityType.CASE_START, [])
    end_rules = ACTIVITY_GDPR_PATTERNS.get(ActivityType.CASE_END, [])

    CASE_START_EVENTS = [
        r["event"]
        for r in start_rules
        if r["condition"](context, r["event"])
    ]

    CASE_END_EVENTS = [
        r["event"]
        for r in end_rules
        if r["condition"](context, r["event"])
    ]

    # ⚠️ nada que hacer
    if not CASE_START_EVENTS and not CASE_END_EVENTS:
        return G

    # =====================================================
    # 1. GUARDAR CONEXIONES
    # =====================================================

    start_targets = list(G.successors(START))
    end_sources = list(G.predecessors(END))

    # =====================================================
    # 2. LIMPIAR
    # =====================================================

    for t in start_targets:
        if G.has_edge(START, t):
            G.remove_edge(START, t)

    for s in end_sources:
        if G.has_edge(s, END):
            G.remove_edge(s, END)

    # =====================================================
    # 3. CASE START
    # =====================================================

    if CASE_START_EVENTS:

        prev = START

        for ev in CASE_START_EVENTS:

            if ev not in G.nodes:
                G.add_node(
                    ev,
                    size=100,
                    color="#d4af37",
                    fontcolor="black",
                    is_gdpr=True,
                    artificial=True
                )

            G.add_edge(prev, ev, weight=1, artificial=True)
            prev = ev

        for t in start_targets:
            G.add_edge(prev, t, weight=1, artificial=True)

    else:
        for t in start_targets:
            G.add_edge(START, t)

    # =====================================================
    # 4. CASE END
    # =====================================================

    if CASE_END_EVENTS:

        next_node = END

        for ev in reversed(CASE_END_EVENTS):

            if ev not in G.nodes:
                G.add_node(
                    ev,
                    size=100,
                    color="#d4af37",
                    fontcolor="black",
                    is_gdpr=True,
                    artificial=True
                )

            G.add_edge(ev, next_node, weight=1, artificial=True)
            next_node = ev

        for s in end_sources:
            G.add_edge(s, next_node, weight=1, artificial=True)

    else:
        for s in end_sources:
            G.add_edge(s, END)

    return G


def connect_start_end(G, start, end, activity_freq):

    # ---------- START ----------
    for node, count in start.items():

        if node not in G.nodes:
            continue

        total = sum(start.values())
        prob = count / total

        if total > 100 and prob < 0.10:
            continue

        G.add_edge(
            START,
            node,
            weight=count,
            width=2
        )

    # ---------- END ----------
    for node, count in end.items():

        if node not in G.nodes:
            continue

        total = activity_freq[node]
        prob = count / total

        if total > 100 and prob < 0.10:
            continue
        elif total > 30 and prob < 0.08:
            continue

        G.add_edge(
            node,
            END,
            weight=count,
            width=2
        )

    return G
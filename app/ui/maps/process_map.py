from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGraphicsTextItem, QGraphicsPathItem, QSlider, QLabel, QFrame
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor, QPainterPath, QBrush, QFont, QPainter, QLinearGradient, QPolygonF
import math
import networkx as nx

class ClickableNode(QGraphicsItem):
    """
    Nodo premium inspirado en Fluxicon Disco (Light Corporate Style). 
    Esquinas redondeadas, relieves suaves y barra de volumen interna visible.
    """
    def __init__(self, node_id, node_data, callback, x, y, width, height):
        super().__init__()
        self.node_id = node_id
        self.node_data = node_data  
        self.callback = callback
        
        self.width = width
        self.height = height
        
        # Geometría local centrada
        self.rect_path = QPainterPath()
        self.rect_path.addRoundedRect(-width / 2, -height / 2, width, height, 5, 5)
        
        # Colores dinámicos adaptados a fondo claro (Estilo Disco Clásico)
        hex_color = node_data.get("fillcolor", "#3164a6")  # Azul Disco por defecto
        if hex_color.startswith("rgba") or hex_color == "#1f2937":
            self.base_color = QColor("#3164a6")
        else:
            self.base_color = QColor(hex_color)
            
        self.hover_color = self.base_color.lighter(115)
        self.current_brush = QBrush(self.base_color)
        
        # Contornos suaves de los nodos
        self.pen = QPen(self.base_color.darker(120), 1.2)
        if node_data.get("is_gdpr") or "verify" in str(node_id).lower() or "consent" in str(node_id).lower():
            self.pen = QPen(QColor("#e67e22"), 2, Qt.PenStyle.SolidLine)  # Alerta GDPR Naranja Disco
            
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

    def boundingRect(self):
        return self.rect_path.boundingRect().adjusted(-10, -10, 10, 10)

    def shape(self):
        return self.rect_path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Sombra sutil difuminada (Muy ligera para fondos claros)
        painter.setBrush(QBrush(QColor(0, 0, 0, 20)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(-self.width / 2 + 3, -self.height / 2 + 3, self.width, self.height, 5, 5)

        # Gradiente suave tipo "Glossy" corporativo de Disco
        gradient = QLinearGradient(0, -self.height/2, 0, self.height/2)
        gradient.setColorAt(0.0, self.current_brush.color().lighter(106))
        gradient.setColorAt(1.0, self.current_brush.color().darker(104))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(self.pen)
        painter.drawPath(self.rect_path)
        
        # Indicador inferior de volumen / importancia relativa
        importance = float(self.node_data.get("importance", 0.5))
        indicator_width = (self.width - 16) * importance
        painter.setBrush(QBrush(QColor(255, 255, 255, 130)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(-self.width / 2 + 8, self.height / 2 - 6, indicator_width, 2.5, 1, 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.callback:
            self.callback(self.node_id, self.node_data)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self.current_brush = QBrush(self.hover_color)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.current_brush = QBrush(self.base_color)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)


class ProcessMap(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- PANEL DE CONTROLES LATERAL (ESTILO DISCO GRIS CLARO) ---
        self.sidebar_sliders = QFrame()
        self.sidebar_sliders.setFixedWidth(75)
        self.sidebar_sliders.setStyleSheet("""
            QFrame { background-color: #eaedf1; border-right: 1px solid #cbd5e1; }
            QLabel { color: #475569; font-size: 10px; font-weight: bold; font-family: 'Segoe UI', sans-serif; }
            QSlider::groove:vertical { background: #cbd5e1; width: 4px; border-radius: 2px; }
            QSlider::sub-page:vertical { background: #cbd5e1; border-radius: 2px; }
            QSlider::add-page:vertical { background: #3164a6; border-radius: 2px; }
            QSlider::handle:vertical { background: #ffffff; border: 1px solid #3164a6; height: 14px; width: 14px; margin: 0 -5px; border-radius: 7px; }
            QSlider::handle:vertical:hover { background: #3164a6; }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar_sliders)
        sidebar_layout.setContentsMargins(8, 20, 8, 20)
        
        lbl_nodes = QLabel("ACTIV.")
        lbl_nodes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_nodes = QSlider(Qt.Orientation.Vertical)
        self.slider_nodes.setRange(10, 100)
        self.slider_nodes.setValue(100)
        self.slider_nodes.valueChanged.connect(self.draw_graph)
        
        lbl_paths = QLabel("PATHS")
        lbl_paths.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_paths = QSlider(Qt.Orientation.Vertical)
        self.slider_paths.setRange(0, 100)
        self.slider_paths.setValue(0) 
        self.slider_paths.valueChanged.connect(self.draw_graph)

        sidebar_layout.addWidget(lbl_nodes)
        sidebar_layout.addWidget(self.slider_nodes, stretch=1)
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(lbl_paths)
        sidebar_layout.addWidget(self.slider_paths, stretch=1)

        # --- VIEWPORT DEL GRAFO (FONDO CLARO TOTALMENTE LEGIBLE) ---
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHints(
            QPainter.RenderHint.Antialiasing | 
            QPainter.RenderHint.TextAntialiasing | 
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Fondo gris claro / blanco roto corporativo para contrastar las líneas oscuras
        self.view.setStyleSheet("background-color: #f5f7fa; border: none;")

        main_layout.addWidget(self.sidebar_sliders)
        main_layout.addWidget(self.view, stretch=1)
        self.setLayout(main_layout)

        self.graph = None
        self.node_click_callback = None

    def set_graph(self, graph):
        self.graph = graph
        self.draw_graph()

    def compute_layout(self, graph):
        try:
            from app.ui.maps.layout_algorithm import disco_layout, compute_node_importance
            pos = disco_layout(graph)
            importance = compute_node_importance(graph)
        except ImportError:
            pos = nx.drawing.layout.kamada_kawai_layout(graph, scale=400)
            importance = nx.degree_centrality(graph)
            
        for n in graph.nodes:
            graph.nodes[n]["importance"] = importance.get(n, 0.5)
        return pos

    def draw_graph(self):
        if self.graph is None:
            return

        self.scene.clear()
        graph = self.graph.copy()

        # 1. FILTRADO DE NODOS
        cutoff_node_perc = self.slider_nodes.value() / 100.0
        importance_dict = {n: graph.degree(n, weight='weight') for n in graph.nodes if n not in ["START", "END"]}
        if importance_dict:
            sorted_nodes = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            num_to_keep = int(len(sorted_nodes) * cutoff_node_perc)
            nodes_to_keep = set([n for n, _ in sorted_nodes[:num_to_keep]] + ["START", "END"])
            graph.remove_nodes_from([n for n in graph.nodes if n not in nodes_to_keep])

        # 2. FILTRADO DE ARISTAS
        weights = [d.get("weight", 1) for _, _, d in graph.edges(data=True)]
        edge_threshold = sorted(weights)[int((len(weights) - 1) * (self.slider_paths.value() / 100.0))] if weights else 0

        pos = self.compute_layout(graph)
        node_items = {}
        main_edges = self.compute_main_path_edges(graph)

        node_w, node_h = 140, 42

        # ---------------- RENDERIZAR NODOS ----------------
        for node, (x, y) in pos.items():
            node_data = graph.nodes[node]
            
            if node == "START":
                node_data["fillcolor"] = "#2ea44f"  # Verde Disco
                node_data["fontcolor"] = "#ffffff"
            elif node == "END":
                node_data["fillcolor"] = "#cf222e"  # Rojo Disco
                node_data["fontcolor"] = "#ffffff"

            rect = ClickableNode(node, node_data, self.node_click_callback, x, y, node_w, node_h)
            self.scene.addItem(rect)

            display_name = node_data.get("label", str(node))
            hex_text_color = node_data.get("fontcolor", "#ffffff") # Texto blanco para contrastar cajas de color
            
            freq = node_data.get("frequency", node_data.get("frecuencia", ""))
            freq_str = f"<br><span style='font-size: 8px; color: #e2e8f0; font-weight: normal;'>{freq}</span>" if freq else ""
            
            label = QGraphicsTextItem()
            label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            label.setDefaultTextColor(QColor(hex_text_color))
            label.setHtml(f"<div align='center' style='line-height: 105%;'>{display_name}{freq_str}</div>")
            label.setTextWidth(node_w - 10)
            
            label.setPos(x - (node_w - 10) / 2, y - label.boundingRect().height() / 2)
            label.setZValue(25)
            self.scene.addItem(label)

            node_items[node] = (x, y)

        # ---------------- RENDERIZAR ARISTAS (CONTRASTE CLARO) ----------------
        max_weight = max(weights, default=1)

        for u, v, data in graph.edges(data=True):
            if u not in node_items or v not in node_items:
                continue
            
            weight = data.get("weight", 1)
            is_main = (u, v) in main_edges
            
            if weight < edge_threshold and not is_main:
                continue 

            x1, y1 = node_items[u]
            x2, y2 = node_items[v]

            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0: 
                continue

            scale_x = (node_w / 2 + 2) / abs(dx) if dx != 0 else float('inf')
            scale_y = (node_h / 2 + 2) / abs(dy) if dy != 0 else float('inf')
            t_border = min(scale_x, scale_y)
            
            start_x, start_y = x1 + dx * t_border, y1 + dy * t_border
            end_x, end_y = x2 - dx * t_border, y2 - dy * t_border

            curve_path = QPainterPath()
            curve_path.moveTo(QPointF(start_x, start_y))
            
            if is_main:
                ctrl1 = QPointF(start_x + dx * 0.1, start_y + dy * 0.4)
                ctrl2 = QPointF(start_x + dx * 0.4, start_y + dy * 0.8)
            else:
                offset_side = 45 if dx >= 0 else -45
                ctrl1 = QPointF(start_x + dx * 0.2 + offset_side, start_y + dy * 0.3)
                ctrl2 = QPointF(start_x + dx * 0.6 + offset_side, start_y + dy * 0.7)

            curve_path.cubicTo(ctrl1, ctrl2, QPointF(end_x, end_y))
            
            edge_item = QGraphicsPathItem(curve_path)
            edge_thickness = 1.2 + (math.log(weight + 1) * 1.4 if max_weight > 1 else 1)
            
            # Paleta de flujos en fondo claro: Gris oscuro azulado / Grafito para máxima definición
            if is_main:
                color_vector = QColor("#2c3e50")  # Grafito oscuro elegante
                edge_item.setOpacity(0.9)
            else:
                color_vector = QColor("#7f8c8d")  # Gris medio secundario
                edge_item.setOpacity(0.5)
                
            pen = QPen(color_vector, edge_thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            edge_item.setPen(pen)
            edge_item.setZValue(5)
            self.scene.addItem(edge_item)

            # --- PUNTA DE FLECHA ---
            t_prev = curve_path.pointAtPercent(0.95)
            t_end = curve_path.pointAtPercent(1.0)
            tan_angle = math.atan2(t_end.y() - t_prev.y(), t_end.x() - t_prev.x())

            arrow_size = 6 + edge_thickness * 0.5
            arrow_angle = math.pi / 6 
            
            arrow_p1 = QPointF(
                end_x - arrow_size * math.cos(tan_angle - arrow_angle),
                end_y - arrow_size * math.sin(tan_angle - arrow_angle)
            )
            arrow_p2 = QPointF(
                end_x - arrow_size * math.cos(tan_angle + arrow_angle),
                end_y - arrow_size * math.sin(tan_angle + arrow_angle)
            )

            arrow_head = QPolygonF([QPointF(end_x, end_y), arrow_p1, arrow_p2])
            arrow_item = self.scene.addPolygon(arrow_head, QPen(Qt.PenStyle.NoPen), QBrush(color_vector))
            arrow_item.setZValue(6)
            arrow_item.setOpacity(edge_item.opacity())

            # --- ETIQUETA DE FLUJO NUMÉRICA LIMPIA (FONDO BLANCO TRANSLÚCIDO) ---
            mx, my = curve_path.pointAtPercent(0.5).x(), curve_path.pointAtPercent(0.5).y()
            label_edge = QGraphicsTextItem()
            label_edge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            label_edge.setDefaultTextColor(QColor("#1e293b"))
            
            # Ahora el micro-borde es blanco para camuflar el paso de la línea en el lienzo claro
            label_edge.setHtml(f"<div style='background-color: rgba(255, 255, 255, 0.9); padding: 1px 3px; border: 1px solid #cbd5e1; border-radius: 3px;'>{weight}</div>")
            label_edge.setPos(mx - label_edge.boundingRect().width() / 2, my - label_edge.boundingRect().height() / 2)
            label_edge.setZValue(30)
            self.scene.addItem(label_edge)

        # Ajuste dinámico del Viewport
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-60, -60, 60, 60))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def compute_main_path_edges(self, graph):
        edges = set()
        node = "START"
        visited = set()
        while True:
            if node not in graph: break
            out_edges = list(graph.out_edges(node, data=True))
            if not out_edges: break
            best = max(out_edges, key=lambda x: x[2].get("weight", 1))
            _, nxt, _ = best
            if nxt in visited: break
            edges.add((node, nxt))
            visited.add(node)
            node = nxt
        return edges

    def wheelEvent(self, event):
        zoom = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(zoom, zoom)
        else:
            self.view.scale(1 / zoom, 1 / zoom)

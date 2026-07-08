STYLE = """
/* =====================================================
   VENTANA PRINCIPAL Y CONTENEDORES GENERALES
   ===================================================== */
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: "Segoe UI", "Helvetica Neue", Arial;
    font-size: 13px;
}

/* El Header superior donde dice GDPR PROCESS TRACE ANALYZER */
QFrame#HeaderFrame {
    background-color: #161b22;
    border-bottom: 2px solid #30363d;
    padding: 6px;
}

/* Los títulos "PROCESS MODELS", "LOG MANAGEMENT", etc. */
QLabel#BlockTitle, QLabel#SectionTitle {
    font-size: 14px;
    font-weight: bold;
    color: #00ffaa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

QLabel#InfoText {
    color: #8b949e;
    font-size: 12px;
}

/* Las cajas oscuras que agrupan los botones de la derecha */
QFrame#ToolBlock {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
}

/* Subtítulos pequeños dentro de cada caja de herramientas */
QFrame#ToolBlock QLabel:first-child {
    font-weight: bold;
    color: #58a6ff;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

/* =====================================================
   LISTA DE MODELOS (Panel Izquierdo)
   ===================================================== */
QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    color: #c9d1d9;
}

QListWidget::item:hover {
    background-color: #21262d;
}

QListWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
    font-weight: bold;
}

/* =====================================================
   BOTONES DE LA VENTANA PRINCIPAL (TOOLBOX)
   ===================================================== */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 14px;
    font-weight: 600;
    text-align: left; /* Alineados a la izquierda estilo cyberpunk corporativo */
    margin-top: 4px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    background-color: #0d1117;
    color: #484f58;
    border-color: #21262d;
}

/* =====================================================
   ZONA DE SCROLL Y SUBWIDGETS DE MUTACIONES (Lo que ya tenías)
   ===================================================== */
QScrollArea {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #161b22;
}

QFrame#ScrollContent {
    background-color: #161b22;
}

QComboBox, QSpinBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 9px;
    border: 2px solid #30363d;
    background-color: #21262d;
}

QRadioButton::indicator:checked {
    border-color: #00ffaa;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #00ffaa, stop:0.5 #00ffaa, stop:0.6 transparent);
}

QSlider {
    padding-left: 8px;
    padding-right: 8px;
    background: transparent;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #21262d;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #00ffaa;
    width: 14px;
    height: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #00cc88;
}

QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
}

MutationConfigWidget, RandomMutationWidget {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 10px;
}

/* =====================================================
   AÑADIDOS PARA REPORTES Y TABLAS DE MUTACIÓN
   ===================================================== */

/* Tarjetas de Métricas del Reporte */
QFrame#SummaryCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 15px;
}

/* Tablas Estilizadas */
QTableWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #c9d1d9;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #21262d;
    color: #8b949e;
    padding: 6px;
    border: 1px solid #30363d;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}

/* Estilo para los Badges o textos de Severidad en Tabla */
QLabel#SeverityBadge_VIOLATION {
    color: #ff7b72;
    font-weight: bold;
}

QLabel#SeverityBadge_WARNING {
    color: #d29922;
    font-weight: bold;
}

QLabel#SeverityBadge_OK {
    color: #56d364;
    font-weight: bold;
}

/* Cuadro de texto de detalles de traza (formato log/HTML) */
QTextEdit#LogViewer {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 10px;
}
"""

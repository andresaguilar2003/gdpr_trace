from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QPoint

class HoverStepCard(QFrame):
    """Tarjeta informativa con efectos de animación fluidos al pasar el ratón."""
    def __init__(self, icon, title, desc):
        super().__init__()
        self.setObjectName("StepContainerFrame")
        self.setMinimumHeight(180)
        
        # Estilos base estáticos
        self.setStyleSheet("""
            QFrame#StepContainerFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        
        # Estructura interna
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        s_icon = QLabel(icon)
        s_icon.setStyleSheet("font-size: 26px; background: transparent;")
        
        s_title = QLabel(title)
        s_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #00ffaa; letter-spacing: 0.5px; background: transparent;")
        
        s_desc = QLabel(desc)
        s_desc.setWordWrap(True)
        s_desc.setStyleSheet("font-size: 12px; line-height: 1.4; color: #c9d1d9; background: transparent;")
        
        layout.addWidget(s_icon)
        layout.addWidget(s_title)
        layout.addWidget(s_desc)
        layout.addStretch()

        # Animación de propiedad para simular el escalado/crecimiento en altura
        self.resize_anim = QPropertyAnimation(self, b"minimumHeight")
        self.resize_anim.setDuration(150)
        self.resize_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        """Efecto visual cuando el cursor entra en el bloque."""
        self.setStyleSheet("""
            QFrame#StepContainerFrame {
                background-color: #1f242c;
                border: 1px solid #00ffaa;
                border-radius: 8px;
            }
        """)
        self.resize_anim.stop()
        self.resize_anim.setStartValue(self.height())
        self.resize_anim.setEndValue(195)  # Hacemos zoom vertical simulado aumentando el alto mínimo
        self.resize_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restaurar cuando el cursor sale del bloque."""
        self.setStyleSheet("""
            QFrame#StepContainerFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        self.resize_anim.stop()
        self.resize_anim.setStartValue(self.height())
        self.resize_anim.setEndValue(180)  # Vuelve a su tamaño base
        self.resize_anim.start()
        super().leaveEvent(event)


class WelcomeView(QWidget):
    def __init__(self, on_load_clicked):
        super().__init__()
        self.on_load_clicked = on_load_clicked
        self._is_processing = False  # Flag interno de seguridad
        
        # Layout principal centrado y con márgenes amplios
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(0)
        
        # Contenedor central restrictivo para pantallas grandes
        center_container = QWidget()
        center_container.setMaximumWidth(1000)
        center_layout = QVBoxLayout(center_container)
        center_layout.setSpacing(35)
        
        # =====================================================
        # 1. CABECERA DE BIENVENIDA (TÍTULO MEJORADO)
        # =====================================================
        header_frame = QWidget()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        main_title = QLabel("GDPR PROCESS TRACE ANALYZER")
        # 🚀 Aplicamos un degradado lineal premium con un filtro de iluminación sutil (Glow)
        main_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: 900; 
            letter-spacing: 2px;
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:0.5 #00ffaa, stop:1 #a2ff00);
            background: transparent;
            /* Efecto de relieve en interfaces oscuras */
            qproperty-alignment: 'AlignLeft | AlignVCenter';
        """)
        
        subtitle = QLabel(
            "An enterprise-grade orchestration core to analyze event logs, "
            "inject privacy compliance structures, and stress-test target models via mutation injection."
        )
        subtitle.setObjectName("InfoText")
        subtitle.setStyleSheet("font-size: 14px; line-height: 1.6; color: #8b949e; padding-left: 2px;")
        subtitle.setWordWrap(True)
        
        header_layout.addWidget(main_title)
        header_layout.addWidget(subtitle)
        center_layout.addWidget(header_frame)
        
        # =====================================================
        # 2. SECCIÓN DE PASOS EN HORIZONTAL (CON HOVER DE ZOOM)
        # =====================================================
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(20)
        
        steps_data = [
            ("🧩", "1. DATA INGESTION", "Load execution streams into the analyzer via standardized XES event log datasets."),
            ("🔐", "2. GDPR ENRICHMENT", "Enforce programmatic privacy checkpoints and automatically construct legal workflows."),
            ("🧪", "3. FAULT MUTATION", "Inject calibrated structural errors and privacy anomalies to evaluate detection rules.")
        ]
        
        self.cards = []
        for icon, step_title, step_desc in steps_data:
            step_card = HoverStepCard(icon, step_title, step_desc)
            self.cards.append(step_card)
            steps_layout.addWidget(step_card, stretch=1)
            
        center_layout.addLayout(steps_layout)
        
        # =====================================================
        # 3. ZONA DE IMPORTACIÓN INTERACTIVA (Clickable Total)
        # =====================================================
        self.import_zone = QFrame()
        self.import_zone.setObjectName("DropZoneFrame")
        self.import_zone.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_zone.setStyleSheet("""
            QFrame#DropZoneFrame {
                background-color: #161b22;
                border: 2px dashed #30363d;
                border-radius: 10px;
                padding: 55px;
            }
            QFrame#DropZoneFrame:hover {
                border-color: #58a6ff;
                background-color: #1c2128;
            }
            QFrame#DropZoneFrame:disabled {
                border-color: #21262d;
                background-color: #0d1117;
            }
        """)
        
        # Instalar evento de clic nativo en el contenedor completo
        self.import_zone.mousePressEvent = self._on_zone_clicked
        
        import_layout = QVBoxLayout(self.import_zone)
        import_layout.setSpacing(14)
        import_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        cloud_icon = QLabel("📥")
        cloud_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cloud_icon.setStyleSheet("font-size: 48px; background: transparent;")
        
        upload_prompt = QLabel("Ready to initialize compliance pipelines")
        upload_prompt.setStyleSheet("font-size: 16px; font-weight: 600; color: #c9d1d9; background: transparent;")
        upload_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        upload_subprompt = QLabel("Click anywhere inside this area to browse or drop an IEEE XES dataset (*.xes, *.xes.gz)")
        upload_subprompt.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent;")
        upload_subprompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        import_layout.addWidget(cloud_icon)
        import_layout.addWidget(upload_prompt)
        import_layout.addWidget(upload_subprompt)
        
        center_layout.addWidget(self.import_zone)
        
        # Ajuste de espaciadores elásticos
        main_layout.addStretch(1)
        main_layout.addWidget(center_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)

        # =====================================================
        # 4. CONFIGURACIÓN DE ANIMACIÓN DE ENTRADA (FADE IN)
        # =====================================================
        self.fade_group = QParallelAnimationGroup(self)
        
        # Añadir efecto de opacidad a la cabecera
        self.header_eff = QGraphicsOpacityEffect(header_frame)
        header_frame.setGraphicsEffect(self.header_eff)
        anim_h = QPropertyAnimation(self.header_eff, b"opacity")
        anim_h.setDuration(600)
        anim_h.setStartValue(0.0)
        anim_h.setEndValue(1.0)
        anim_h.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_group.addAnimation(anim_h)
        
        # Añadir efectos de opacidad escalonados a las tarjetas informativas
        for card in self.cards:
            eff = QGraphicsOpacityEffect(card)
            card.setGraphicsEffect(eff)
            anim_c = QPropertyAnimation(eff, b"opacity")
            anim_c.setDuration(750)
            anim_c.setStartValue(0.0)
            anim_c.setEndValue(1.0)
            anim_c.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_group.addAnimation(anim_c)
            
        # Iniciar animaciones de entrada en el primer renderizado
        self.fade_group.start()

    def set_loading_state(self, is_processing):
        """Bloquea o desbloquea la interactividad visual de la zona de importación."""
        self._is_processing = is_processing
        self.import_zone.setEnabled(not is_processing)
        if is_processing:
            self.import_zone.setCursor(Qt.CursorShape.WaitCursor)
        else:
            self.import_zone.setCursor(Qt.CursorShape.PointingHandCursor)

    def _on_zone_clicked(self, event):
        """Manejador de evento de clic."""
        if self._is_processing:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_load_clicked()

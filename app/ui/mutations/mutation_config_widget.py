from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QHBoxLayout
)
from superqt import QRangeSlider

class MutationConfigWidget(QFrame):

    def __init__(self, mutation_name, total_traces):
        super().__init__()

        self.mutation_name = mutation_name
        
        # Asignamos nombres de objeto únicos
        self.setObjectName("CustomMutationCard")
        
        # Estilo premium para la tarjeta contenedora de la mutación
        self.setStyleSheet("""
            QFrame#CustomMutationCard {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
            }
            QFrame#CustomMutationCard:hover {
                border-color: #484f58;
                background-color: #1c2128;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # --- FILA SUPERIOR: Checkbox a la izquierda, Rango a la derecha ---
        top_row = QHBoxLayout()
        
        self.checkbox = QCheckBox(mutation_name)
        self.checkbox.setObjectName("MutationCheckbox")
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 🛠️ SOLUCIÓN DEFINTIVA: Eliminamos url(data:image/svg...) que rompía el parser de Qt.
        # Usamos un indicador estilizado por contenido nativo limpio.
        self.checkbox.setStyleSheet("""
            QCheckBox#MutationCheckbox {
                color: #c9d1d9;
                font-weight: bold;
                font-size: 13px;
                spacing: 8px;
                background: transparent;
            }
            QCheckBox#MutationCheckbox:checked {
                color: #58a6ff;
            }
            QCheckBox#MutationCheckbox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #484f58;
                border-radius: 4px;
                background-color: #0d1117;
            }
            QCheckBox#MutationCheckbox::indicator:hover {
                border-color: #58a6ff;
                background-color: #161b22;
            }
            /* Cuando está seleccionado, usamos una transición de color nativa limpia */
            QCheckBox#MutationCheckbox::indicator:checked {
                border-color: #2ea44f;
                background-color: #2ea44f;
            }
            QCheckBox#MutationCheckbox::indicator:checked:hover {
                border-color: #22863a;
                background-color: #22863a;
            }
        """)

        self.range_label = QLabel(f"TRACES: 0 - {total_traces - 1}")
        self.range_label.setObjectName("MutationRangeLabel")
        self.range_label.setStyleSheet("""
            QLabel#MutationRangeLabel {
                color: #8b949e;
                font-family: monospace;
                font-weight: bold;
                font-size: 11px;
                background-color: #21262d;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid #30363d;
            }
        """)

        top_row.addWidget(self.checkbox)
        top_row.addStretch()
        top_row.addWidget(self.range_label)
        layout.addLayout(top_row)

        # --- FILA INFERIOR: Deslizador de rango estilizado ---
        self.range_slider = QRangeSlider(Qt.Horizontal)
        self.range_slider.setObjectName("MutationSlider")
        self.range_slider.setMinimum(0)
        self.range_slider.setMaximum(total_traces - 1)
        self.range_slider.setValue((0, total_traces - 1))
        self.range_slider.setCursor(Qt.CursorShape.SplitHCursor)
        
        self.range_slider.setStyleSheet("""
            QRangeSlider#MutationSlider {
                height: 22px;
                background: transparent;
            }
            QRangeSlider#MutationSlider::groove:horizontal {
                height: 6px;
                background: #21262d;
                border-radius: 3px;
            }
            QRangeSlider#MutationSlider::sub-page:horizontal {
                background: #30363d;
            }
            QRangeSlider#MutationSlider::add-page:horizontal {
                background: #30363d;
            }
            QRangeSlider#MutationSlider::handle:horizontal {
                background: #58a6ff;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
                border: 1px solid #1f6feb;
            }
            QRangeSlider#MutationSlider::handle:horizontal:hover {
                background: #79c0ff;
            }
        """)

        self.range_slider.valueChanged.connect(self._update_label)
        layout.addWidget(self.range_slider)

    def _update_label(self):
        start, end = self.range_slider.value()
        self.range_label.setText(f"TRACES: {start} - {end}")

    def is_selected(self):
        return self.checkbox.isChecked()

    def get_mutation_name(self):
        return self.mutation_name

    def get_range(self):
        return self.range_slider.value()
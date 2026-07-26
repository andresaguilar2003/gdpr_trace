from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton,
    QRadioButton, QComboBox, QScrollArea, QSpinBox, QSplitter,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.mutations.registry.mutation_registry import MUTATION_REGISTRY
from app.mutations.base.mutation_category import MutationCategory
from app.mutations.services.random_mutation_generator import RandomMutationGenerator
from app.ui.mutations.mutation_config_widget import MutationConfigWidget
from app.ui.mutations.random_mutation_widget import RandomMutationWidget
from app.ui.mutations.mutation_report_window import TraceDetailDialog  # Diálogo de auditoría detallada
from app.ui.main_flow.styles import STYLE


class MutationView(QWidget):
    def __init__(self, on_open_mutations, on_export_mutated, on_back):
        super().__init__()
        
        self.total_traces = 100
        self.widgets = []
        self.random_widgets = []
        self.generated_mutations = []
        self.current_report = None
        self.filtered_reports = []
        self.on_open_mutations = on_open_mutations  # Callback original de inyección
        self.on_export_mutated = on_export_mutated  # Guardamos la referencia para el botón del reporte
        
        self.setStyleSheet(STYLE)
        
        # LAYOUT DE RAÍZ VERTICAL (Permite una barra de navegación superior)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 15, 15, 15)
        root_layout.setSpacing(12)

        # =================================================================
        # BARRA SUPERIOR DE NAVEGACIÓN
        # =================================================================
        nav_bar = QHBoxLayout()
        back_button = QPushButton("⬅ BACK TO ENRICHMENT")
        back_button.setMinimumWidth(200)  # Evita que se colapse el texto
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #8b949e;
            }
        """)
        back_button.clicked.connect(on_back)
        nav_bar.addWidget(back_button)
        nav_bar.addStretch()
        root_layout.addLayout(nav_bar)
        
        # SPLITTER PRINCIPAL (Ahora sí es 100% interactivo y redimensionable)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #30363d;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #58a6ff;
            }
        """)
        
        # =================================================================
        # PANEL IZQUIERDO: CONFIGURADOR DE MUTACIONES
        # =================================================================
        config_panel = QFrame()
        config_panel.setObjectName("ToolBlock")
        config_panel.setMinimumWidth(300) # Ancho mínimo de seguridad, quitamos setFixedWidth
        
        config_layout = QVBoxLayout(config_panel)
        config_layout.setContentsMargins(12, 12, 12, 12)
        config_layout.setSpacing(10)
        
        self.title_label = QLabel("MUTATION ENGINE")
        self.title_label.setObjectName("SectionTitle")
        config_layout.addWidget(self.title_label)

        validation_mode_frame = QFrame()
        validation_mode_frame.setStyleSheet("background-color: #161b22; border-radius: 6px; border: 1px solid #30363d;")
        validation_mode_layout = QVBoxLayout(validation_mode_frame)
        validation_mode_layout.setContentsMargins(8, 8, 8, 8)
        validation_mode_layout.setSpacing(6)

        validation_mode_label = QLabel("VALIDATION MODE")
        validation_mode_label.setStyleSheet("color: #8b949e; font-weight: bold; font-size: 10px;")

        self.validation_mode_combo = QComboBox()
        self.validation_mode_combo.addItem("Deterministic validator", "deterministic")
        self.validation_mode_combo.addItem("T5 AI validator", "ai")
        self.validation_mode_combo.addItem("Both validators", "both")
        self.validation_mode_combo.currentIndexChanged.connect(
            self._update_ai_limit_visibility
        )

        ai_limit_row = QHBoxLayout()
        self.ai_limit_label = QLabel("AI max traces per mutation:")
        self.ai_limit_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        self.ai_limit_spin = QSpinBox()
        self.ai_limit_spin.setMinimum(1)
        self.ai_limit_spin.setMaximum(1000)
        self.ai_limit_spin.setValue(3)

        ai_limit_row.addWidget(self.ai_limit_label)
        ai_limit_row.addWidget(self.ai_limit_spin)

        validation_mode_layout.addWidget(validation_mode_label)
        validation_mode_layout.addWidget(self.validation_mode_combo)
        validation_mode_layout.addLayout(ai_limit_row)
        config_layout.addWidget(validation_mode_frame)
        self._update_ai_limit_visibility()
        
        # Selector de Modos (Manual vs Aleatorio)
        mode_frame = QFrame()
        mode_frame.setStyleSheet("background-color: #161b22; border-radius: 6px; border: 1px solid #30363d;")
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(8, 6, 8, 6)
        
        self.manual_mode = QRadioButton("Manual")
        self.random_mode = QRadioButton("Random")
        self.manual_mode.setChecked(True)
        self.manual_mode.toggled.connect(self._switch_mode)
        
        mode_layout.addWidget(self.manual_mode)
        mode_layout.addWidget(self.random_mode)
        config_layout.addWidget(mode_frame)
        
        # --- SUB-PANEL MANUAL ---
        self.manual_panel = QWidget()
        manual_layout = QVBoxLayout(self.manual_panel)
        manual_layout.setContentsMargins(0, 0, 0, 0)
        manual_layout.setSpacing(8)
        
        cat_row = QHBoxLayout()
        cat_lbl = QLabel("Category:")
        cat_lbl.setStyleSheet("color: #8b949e; font-weight: bold;")
        self.category_combo = QComboBox()
        self.category_combo.addItems([c.name for c in MutationCategory])
        self.category_combo.currentTextChanged.connect(self._reload_mutations)
        cat_row.addWidget(cat_lbl)
        cat_row.addWidget(self.category_combo)
        manual_layout.addLayout(cat_row)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.container = QFrame()
        self.container.setObjectName("ScrollContent")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(2, 2, 2, 2)
        self.container_layout.setSpacing(6)
        self.scroll.setWidget(self.container)
        manual_layout.addWidget(self.scroll)
        
        config_layout.addWidget(self.manual_panel)
        
        # --- SUB-PANEL ALEATORIO ---
        self.random_panel = QWidget()
        random_layout = QVBoxLayout(self.random_panel)
        random_layout.setContentsMargins(0, 0, 0, 0)
        random_layout.setSpacing(8)
        
        rand_row = QHBoxLayout()
        rand_lbl = QLabel("Fault Count:")
        rand_lbl.setStyleSheet("color: #8b949e;")
        self.random_count = QSpinBox()
        self.random_count.setMinimum(1)
        self.random_count.setMaximum(len(MUTATION_REGISTRY) if MUTATION_REGISTRY else 1)
        rand_row.addWidget(rand_lbl)
        rand_row.addWidget(self.random_count)
        random_layout.addLayout(rand_row)
        
        self.random_global = QRadioButton("Apply to entire dataset")
        self.random_custom = QRadioButton("Manual ranges per trace")
        self.random_global.setChecked(True)
        random_layout.addWidget(self.random_global)
        random_layout.addWidget(self.random_custom)
        
        self.generate_rand_button = QPushButton("🎲 Generate Fault Matrix")
        self.generate_rand_button.setObjectName("SecondaryButton")
        self.generate_rand_button.clicked.connect(self._generate_random_mutations)
        random_layout.addWidget(self.generate_rand_button)
        
        self.random_scroll = QScrollArea()
        self.random_scroll.setWidgetResizable(True)
        self.random_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.random_content = QFrame()
        self.random_content.setObjectName("ScrollContent")
        self.random_container = QVBoxLayout(self.random_content)
        self.random_container.setContentsMargins(2, 2, 2, 2)
        self.random_container.setSpacing(6)
        self.random_scroll.setWidget(self.random_content)
        random_layout.addWidget(self.random_scroll)
        
        config_layout.addWidget(self.random_panel)
        self.random_panel.hide()
        
        # Footer del panel izquierdo
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #30363d; max-height: 1px; border: none; margin: 5px 0;")
        config_layout.addWidget(line)
        
        # BOTÓN PRINCIPAL DE ACCIÓN: INYECTAR MUTACIONES (Optimizado visualmente)
        self.mutation_button = QPushButton("🧪 INJECT GDPR VIOLATIONS")
        self.mutation_button.setStyleSheet("""
            QPushButton {
                background-color: #d1440c;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #f26522;
                border-radius: 6px;
                padding: 10px 15px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #e0531c;
                border-color: #f47942;
            }
            QPushButton:pressed {
                background-color: #a7360a;
            }
        """)
        self.mutation_button.clicked.connect(self._on_inject_clicked)
        config_layout.addWidget(self.mutation_button)
        
        # =================================================================
        # PANEL DERECHO: REPORTE E INTERFAZ DE AUDITORÍA INTEGRADA
        # =================================================================
        self.report_panel = QFrame()
        self.report_panel.setObjectName("MainContainerPanel")
        self.report_panel.setMinimumWidth(500)
        self.report_panel.setStyleSheet("background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px;")
        
        self.report_layout = QVBoxLayout(self.report_panel)
        self.report_layout.setContentsMargins(20, 20, 20, 20)
        self.report_layout.setSpacing(12)
        
        # Estado inicial vacío (Placeholder)
        self.placeholder_layout = QVBoxLayout()
        self.placeholder_layout.setAlignment(Qt.AlignCenter)
        
        self.icon_placeholder = QLabel("🧪")
        self.icon_placeholder.setStyleSheet("font-size: 50px; margin-bottom: 10px;")
        self.icon_placeholder.setAlignment(Qt.AlignCenter)
        
        self.txt_placeholder = QLabel("Awaiting Fault Injection Configuration...\nSelect anomalies on the left panel and click 'Inject'.")
        self.txt_placeholder.setStyleSheet("color: #8b949e; font-size: 14px; text-align: center; line-height: 1.5;")
        self.txt_placeholder.setAlignment(Qt.AlignCenter)
        
        self.placeholder_layout.addWidget(self.icon_placeholder)
        self.placeholder_layout.addWidget(self.txt_placeholder)
        self.report_layout.addLayout(self.placeholder_layout)
        
        # Añadir elementos al splitter y setear pesos de estiramiento iniciales (35% - 65%)
        splitter.addWidget(config_panel)
        splitter.addWidget(self.report_panel)
        splitter.setStretchFactor(0, 35)
        splitter.setStretchFactor(1, 65)
        
        root_layout.addWidget(splitter)

    # =================================================================
    # MANEJO DE ACCIONES Y VALIDACIONES
    # =================================================================
    
    def _on_inject_clicked(self):
        """Intercepta el clic de inyección para validar la entrada manual."""
        if self.manual_mode.isChecked():
            # Comprobar si hay al menos un widget de mutación seleccionado
            has_selection = any(w.is_selected() for w in self.widgets)
            if not has_selection:
                QMessageBox.warning(
                    self,
                    "No Mutations Selected",
                    "Please select at least one mutation rule checkbox from the list before attempting injection."
                )
                return
        
        # Si la validación pasa (o es modo Random), se ejecuta el callback original
        if (
            self.get_validation_mode() in {"ai", "both"}
            and self._selected_evaluation_count() > self.ai_limit_spin.value()
        ):
            QMessageBox.information(
                self,
                "AI validation limit",
                (
                    "T5 validation is limited to the first "
                    f"{self.ai_limit_spin.value()} selected traces per mutation "
                    "to keep the interface responsive. Increase the limit if "
                    "you want to test more traces."
                )
            )

        self.on_open_mutations()

    def setup_mutation_config(self, model_name, total_traces):
        self.total_traces = total_traces
        self.ai_limit_spin.setMaximum(max(1, total_traces))
        self.ai_limit_spin.setValue(
            min(self.ai_limit_spin.value(), max(1, total_traces))
        )
        self.title_label.setText(f"MUTATIONS · {model_name.split('·')[-1].strip()}")
        self._reload_mutations()

    def _switch_mode(self):
        manual = self.manual_mode.isChecked()
        self.manual_panel.setVisible(manual)
        self.random_panel.setVisible(not manual)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
            elif item.spacerItem():
                del item

    def _reload_mutations(self):
        self._clear_layout(self.container_layout)
        self.widgets.clear()
        category = self.category_combo.currentText()

        for name, data in MUTATION_REGISTRY.items():
            if data["category"].name != category:
                continue

            widget = MutationConfigWidget(name, self.total_traces)
            widget.setStyleSheet(STYLE) 
            self.widgets.append(widget)
            self.container_layout.addWidget(widget)

        self.container_layout.addStretch()

    def _generate_random_mutations(self):
        self._clear_layout(self.random_container)
        self.random_widgets.clear()
        
        count = self.random_count.value()
        self.generated_mutations = RandomMutationGenerator.generate(count)

        if self.random_global.isChecked():
            for mutation in self.generated_mutations:
                lbl = QLabel(f" ✓  {mutation}")
                lbl.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 12px; padding: 2px;")
                self.random_container.addWidget(lbl)
        else:
            for mutation in self.generated_mutations:
                widget = RandomMutationWidget(mutation, self.total_traces)
                widget.setStyleSheet(STYLE)
                self.random_widgets.append(widget)
                self.random_container.addWidget(widget)
                
        self.random_container.addStretch()

    def get_selected_configs(self):
        configs = []
        if self.manual_mode.isChecked():
            for widget in self.widgets:
                if not widget.is_selected():
                    continue
                start, end = widget.get_range()
                configs.append({
                    "mutation": widget.get_mutation_name(),
                    "start": start,
                    "end": end
                })
        else:
            if self.random_global.isChecked():
                for mutation in self.generated_mutations:
                    configs.append({
                        "mutation": mutation,
                        "start": 0,
                        "end": self.total_traces - 1
                    })
            else:
                for widget in self.random_widgets:
                    start, end = widget.get_range()
                    configs.append({
                        "mutation": widget.mutation_name,
                        "start": start,
                        "end": end
                    })
        return self._limit_ai_configs(configs)

    def get_validation_mode(self):
        return self.validation_mode_combo.currentData()

    def _update_ai_limit_visibility(self):
        ai_mode = self.get_validation_mode() in {"ai", "both"}
        self.ai_limit_label.setVisible(ai_mode)
        self.ai_limit_spin.setVisible(ai_mode)

    def _limit_ai_configs(self, configs):
        if self.get_validation_mode() == "deterministic":
            return configs

        max_per_mutation = self.ai_limit_spin.value()
        limited = []

        for config in configs:
            start = config["start"]
            end = config["end"]
            count = end - start + 1

            if count <= max_per_mutation:
                limited.append(config)
                continue

            limited_config = dict(config)
            limited_config["end"] = start + max_per_mutation - 1
            limited.append(limited_config)

        return limited

    def _selected_evaluation_count(self):
        count = 0

        if self.manual_mode.isChecked():
            for widget in self.widgets:
                if not widget.is_selected():
                    continue

                start, end = widget.get_range()
                count += end - start + 1

            return count

        if self.random_global.isChecked():
            return len(self.generated_mutations) * max(1, self.total_traces)

        for widget in self.random_widgets:
            start, end = widget.get_range()
            count += end - start + 1

        return count

    # =================================================================
    # INTERFAZ DEL REPORTE INTEGRADO Y COMPLETO
    # =================================================================
    
    def display_report(self, report):
        """Procesa y renderiza el dashboard de cumplimiento con tabla y filtros dinámicos."""
        self.clear_report_view()
        self.current_report = report
        
        # Ocultar placeholder
        self.icon_placeholder.hide()
        self.txt_placeholder.hide()
        
        # --- ENCABEZADO DEL REPORTE CON BOTÓN DE EXPORTACIÓN CONTEXTUAL ---
        header_container = QHBoxLayout()
        rep_title = QLabel("GDPR COMPLIANCE & MUTATION AUDIT REPORT")
        rep_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #58a6ff; letter-spacing: 0.5px;")
        
        self.export_mutated_button = QPushButton("☠ EXPORT NON-COMPLIANT LOG")
        self.export_mutated_button.setObjectName("PrimaryButton")
        self.export_mutated_button.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #2ea043; }
        """)
        self.export_mutated_button.clicked.connect(self.on_export_mutated)
        
        header_container.addWidget(rep_title)
        header_container.addStretch()
        header_container.addWidget(self.export_mutated_button)
        self.report_layout.addLayout(header_container)
        
        # Dashboard de KPIs resumidos
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        cards_data = [
            ("MUTATED TRACES", str(report.total_mutated_traces), "#58a6ff", "#161b22"),
            ("CRITICAL VIOLATIONS", str(report.total_violations), "#ff7b72", "#211515"),
            ("SECURITY WARNINGS", str(report.total_warnings), "#d29922", "#1e1a10")
        ]
        
        for title, val, color, bg in cards_data:
            card = QFrame()
            card.setStyleSheet(f"background-color: {bg}; border: 1px solid {color}; border-radius: 6px; padding: 10px;")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(8, 8, 8, 8)
            
            lbl_t = QLabel(f"<span style='color:#8b949e; font-size:10px; font-weight:bold;'>{title}</span>")
            lbl_v = QLabel(f"<span style='font-size:22px; font-weight:bold; color:{color};'>{val}</span>")
            
            c_lay.addWidget(lbl_t)
            c_lay.addWidget(lbl_v)
            stats_layout.addWidget(card)
            
        self.report_layout.addLayout(stats_layout)
        
        # Barra de Filtros Integrada
        filters_container = QFrame()
        filters_container.setStyleSheet("background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 4px;")
        filters_layout = QHBoxLayout(filters_container)
        filters_layout.setContentsMargins(8, 4, 8, 4)
        filters_layout.setSpacing(8)
        
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["ALL", "VIOLATION", "WARNING", "COMPLIANT"])
        self.severity_filter.currentTextChanged.connect(self._populate_table)
        
        self.mutation_filter = QComboBox()
        mutations = sorted(set(r.mutation_name for r in report.trace_reports))
        self.mutation_filter.addItem("ALL")
        self.mutation_filter.addItems(mutations)
        self.mutation_filter.currentTextChanged.connect(self._populate_table)
        
        filters_layout.addWidget(QLabel("Severity:"))
        filters_layout.addWidget(self.severity_filter)
        filters_layout.addWidget(QLabel("Mutation Rule:"))
        filters_layout.addWidget(self.mutation_filter)
        filters_layout.addWidget(QLabel("<span style='color:#8b949e; font-size:11px; margin-left:10px;'>💡 Double-click row to open trail logs</span>"))
        filters_layout.addStretch()
        
        self.report_layout.addWidget(filters_container)
        
        # Tabla Principal del Reporte
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Trace Target ID",
            "Applied Mutation Engine",
            "Validator",
            "AI Impact",
            "Audit Status",
            "Violations",
            "Warnings",
            "Agreement"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #1c2128; }")
        self.table.cellDoubleClicked.connect(self._open_trace_detail)
        
        self.report_layout.addWidget(self.table)
        
        # Llenar la tabla con los datos por primera vez
        self._populate_table()

    def _populate_table(self):
        if not self.current_report:
            return
            
        severity_filter = self.severity_filter.currentText()
        mutation_filter = self.mutation_filter.currentText()

        filtered = []
        for r in self.current_report.trace_reports:
            report_severity = self._display_severity(r.severity)
            if severity_filter != "ALL" and report_severity != severity_filter:
                continue
            if mutation_filter != "ALL" and r.mutation_name != mutation_filter:
                continue
            filtered.append(r)

        self.filtered_reports = filtered
        self.table.setRowCount(len(filtered))

        for row, r in enumerate(filtered):
            v_count = len(r.validator_result.get("violations", []))
            w_count = len(r.validator_result.get("warnings", []))
            validation_mode = r.validator_result.get("validation_mode", "deterministic")
            agreement = r.validator_result.get("agrees_with_ai")
            impact_text = self._impact_text(r.validator_result)
            impact_color = self._impact_color(impact_text)
            display_severity = self._display_severity(r.severity)

            # Trace ID
            item_id = QTableWidgetItem(str(r.trace_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            
            # Mutation Name
            item_mut = QTableWidgetItem(r.mutation_name)

            item_mode = QTableWidgetItem(validation_mode.upper())
            item_mode.setTextAlignment(Qt.AlignCenter)

            item_impact = QTableWidgetItem(impact_text)
            item_impact.setTextAlignment(Qt.AlignCenter)
            item_impact.setForeground(impact_color)
            
            # Status Badge
            item_sev = QTableWidgetItem(f" ● {r.severity}")
            item_sev.setText(f" ● {display_severity}")
            if display_severity == "VIOLATION":
                item_sev.setForeground(Qt.GlobalColor.red)
            elif display_severity == "WARNING":
                item_sev.setForeground(Qt.GlobalColor.yellow)
            else:
                item_sev.setForeground(Qt.GlobalColor.green)
            font_bold = QFont()
            font_bold.setBold(True)
            item_sev.setFont(font_bold)

            # Violaciones
            item_v = QTableWidgetItem(str(v_count))
            item_v.setTextAlignment(Qt.AlignCenter)
            if v_count > 0:
                item_v.setForeground(Qt.GlobalColor.red)

            # Warnings
            item_w = QTableWidgetItem(str(w_count))
            item_w.setTextAlignment(Qt.AlignCenter)
            if w_count > 0:
                item_w.setForeground(Qt.GlobalColor.yellow)

            if agreement is None:
                agreement_text = "-"
            else:
                agreement_text = "YES" if agreement else "NO"

            item_agreement = QTableWidgetItem(agreement_text)
            item_agreement.setTextAlignment(Qt.AlignCenter)
            if agreement is True:
                item_agreement.setForeground(Qt.GlobalColor.green)
            elif agreement is False:
                item_agreement.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, item_mut)
            self.table.setItem(row, 2, item_mode)
            self.table.setItem(row, 3, item_impact)
            self.table.setItem(row, 4, item_sev)
            self.table.setItem(row, 5, item_v)
            self.table.setItem(row, 6, item_w)
            self.table.setItem(row, 7, item_agreement)

        self.table.resizeColumnsToContents()

    @staticmethod
    def _display_severity(severity):
        return "COMPLIANT" if severity == "OK" else severity

    @staticmethod
    def _impact_text(validator_result):
        impact = validator_result.get("impact")

        if not impact and validator_result.get("ai_result"):
            impact = validator_result["ai_result"].get("impact")

        return impact or "-"

    @staticmethod
    def _impact_color(impact):
        if impact == "0_COMPLIANT":
            return Qt.GlobalColor.green

        if impact == "1_VIOLATION":
            return Qt.GlobalColor.red

        if impact == "2_WARNING":
            return Qt.GlobalColor.yellow

        return Qt.GlobalColor.gray

    def _open_trace_detail(self, row, column):
        report = self.filtered_reports[row]
        dialog = TraceDetailDialog(report)
        dialog.exec()

    def clear_report_view(self):
        """Limpia todo el layout del panel derecho eliminando widgets dinámicos y recupera el placeholder."""
        self.current_report = None
        self.filtered_reports.clear()
        
        for i in reversed(range(self.report_layout.count())):
            item = self.report_layout.itemAt(i)
            if item.layout() == self.placeholder_layout:
                continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                
        self.icon_placeholder.show()
        self.txt_placeholder.show()

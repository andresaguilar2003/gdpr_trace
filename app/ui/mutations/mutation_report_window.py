from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QTableWidget, QTableWidgetItem, QTextEdit, QDialog, QPushButton, QFrame
)

class TraceDetailDialog(QDialog):

    def __init__(self, trace_report):
        super().__init__()

        self.setWindowTitle(f"📊 Trace Violation Audit · ID {trace_report.trace_id}")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # =====================================================
        # HEADER INFO BLOCK
        # =====================================================
        info_block = QFrame()
        info_block.setObjectName("ToolBlock")
        info_layout = QVBoxLayout(info_block)
        info_layout.setSpacing(6)

        mutation_lbl = QLabel(f"🧬 MUTATION EFFECT: <span style='color:#58a6ff; font-weight:bold;'>{trace_report.mutation_name}</span>")
        mutation_lbl.setTextFormat(Qt.RichText)
        
        # Color dinámico de severidad
        sev_color = "#ff7b72" if trace_report.severity == "VIOLATION" else "#d29922" if trace_report.severity == "WARNING" else "#56d364"
        severity_lbl = QLabel(f"⚠️ SEVERITY: <span style='color:{sev_color}; font-weight:bold;'>{trace_report.severity}</span>")
        severity_lbl.setTextFormat(Qt.RichText)

        validation_mode = trace_report.validator_result.get("validation_mode", "deterministic")
        mode_lbl = QLabel(f"VALIDATOR: <span style='color:#58a6ff; font-weight:bold;'>{validation_mode.upper()}</span>")
        mode_lbl.setTextFormat(Qt.RichText)

        agreement = trace_report.validator_result.get("agrees_with_ai")
        agreement_lbl = None
        if agreement is not None:
            agreement_color = "#56d364" if agreement else "#d29922"
            agreement_lbl = QLabel(f"AI AGREEMENT: <span style='color:{agreement_color}; font-weight:bold;'>{'YES' if agreement else 'NO'}</span>")
            agreement_lbl.setTextFormat(Qt.RichText)

        rec_lbl = QLabel(f"💡 <b>RECOMMENDATION:</b><br><span style='color:#8b949e;'>{trace_report.recommendation}</span>")
        rec_lbl.setWordWrap(True)
        rec_lbl.setTextFormat(Qt.RichText)

        info_layout.addWidget(mutation_lbl)
        info_layout.addWidget(mode_lbl)
        if agreement_lbl:
            info_layout.addWidget(agreement_lbl)
        info_layout.addWidget(severity_lbl)
        info_layout.addWidget(rec_lbl)
        layout.addWidget(info_block)

        # =====================================================
        # DETAILS (HTML AUDIT LOG)
        # =====================================================
        title_details = QLabel("AUDIT TRAIL LOG")
        title_details.setObjectName("SectionTitle")
        layout.addWidget(title_details)

        details = QTextEdit()
        details.setObjectName("LogViewer")
        details.setReadOnly(True)

        html_content = ["<body style='color:#c9d1d9; font-family:monospace;'>"]

        violations = trace_report.validator_result.get("violations", [])
        warnings = trace_report.validator_result.get("warnings", [])

        # --- VIOLATIONS SECTION ---
        html_content.append("<b style='color:#ff7b72; font-size:13px;'>🚨 CRITICAL VIOLATIONS DETECTED</b>")
        html_content.append("<hr style='border: 1px solid #30363d;'>")
        if violations:
            for v in violations:
                html_content.append(f"<div style='margin-bottom: 10px; background-color: #2c1919; padding: 8px; border-left: 4px solid #ff7b72; border-radius:4px;'>")
                html_content.append(f"  <b style='color:#ff9e96;'>[RULE]:</b> {v['rule']}<br>")
                html_content.append(f"  <b>[EVENT]:</b> <span style='color:#ff7b72;'>{v['event']}</span><br>")
                html_content.append(f"  <b>[DETAILS]:</b> {v.get('message', '')}")
                html_content.append(f"</div>")
        else:
            html_content.append("<p style='color:#8b949e; italic;'>No critical compliance mutations broke strict rules.</p>")

        html_content.append("<br>")

        # --- WARNINGS SECTION ---
        html_content.append("<b style='color:#d29922; font-size:13px;'>⚠️ PRIVACY WARNINGS / ANOMALIES</b>")
        html_content.append("<hr style='border: 1px solid #30363d;'>")
        if warnings:
            for w in warnings:
                html_content.append(f"<div style='margin-bottom: 10px; background-color: #2c2414; padding: 8px; border-left: 4px solid #d29922; border-radius:4px;'>")
                html_content.append(f"  <b style='color:#f0e084;'>[RULE]:</b> {w['rule']}<br>")
                html_content.append(f"  <b>[EVENT]:</b> <span style='color:#d29922;'>{w['event']}</span><br>")
                html_content.append(f"  <b>[DETAILS]:</b> {w.get('message', '')}")
                html_content.append(f"</div>")
        else:
            html_content.append("<p style='color:#8b949e; italic;'>No secondary warnings found for this trace execution.</p>")

        ai_result = trace_report.validator_result.get("ai_result")

        if ai_result:
            html_content.append("<br>")
            html_content.append("<b style='color:#58a6ff; font-size:13px;'>T5 AI VALIDATOR OUTPUT</b>")
            html_content.append("<hr style='border: 1px solid #30363d;'>")
            html_content.append(f"<p><b>Raw:</b> {ai_result.get('rawResponse', '')}</p>")

            ai_violations = ai_result.get("violations", [])
            ai_warnings = ai_result.get("warnings", [])

            html_content.append("<b>AI violations:</b>")
            if ai_violations:
                for v in ai_violations:
                    html_content.append(f"<p>- {v.get('rule')} @ {v.get('event')}</p>")
            else:
                html_content.append("<p style='color:#8b949e;'>- none</p>")

            html_content.append("<b>AI warnings:</b>")
            if ai_warnings:
                for w in ai_warnings:
                    html_content.append(f"<p>- {w.get('rule')} @ {w.get('event')}</p>")
            else:
                html_content.append("<p style='color:#8b949e;'>- none</p>")

        html_content.append("</body>")
        details.setHtml("\n".join(html_content))
        layout.addWidget(details)

        # Bottom Bar
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        close_button = QPushButton("✕ CLOSE AUDIT")
        close_button.setFixedWidth(130)
        close_button.clicked.connect(self.close)
        actions_layout.addWidget(close_button)
        
        layout.addLayout(actions_layout)


class MutationReportWindow(QWidget):

    def __init__(self, report):
        super().__init__()
        self.report = report
        self.setWindowTitle("Mutation Analysis & GDPR Compliance Report")
        self.resize(1200, 750)

        self._build_ui()
        self._populate_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # =================================================
        # SUMMARY CARDS PANEL
        # =================================================
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(12)

        card_traces = QFrame()
        card_traces.setObjectName("SummaryCard")
        lt1 = QVBoxLayout(card_traces)
        lt1.addWidget(QLabel("<span style='color:#8b949e; font-size:10px; font-weight:bold;'>MUTATED TRACES</span>"))
        lt1.addWidget(QLabel(f"<span style='font-size:20px; font-weight:bold; color:#58a6ff;'>{self.report.total_mutated_traces}</span>"))

        card_violations = QFrame()
        card_violations.setObjectName("SummaryCard")
        card_violations.setStyleSheet("border-left: 3px solid #ff7b72;")
        lt2 = QVBoxLayout(card_violations)
        lt2.addWidget(QLabel("<span style='color:#8b949e; font-size:10px; font-weight:bold;'>TOTAL VIOLATIONS</span>"))
        lt2.addWidget(QLabel(f"<span style='font-size:20px; font-weight:bold; color:#ff7b72;'>{self.report.total_violations}</span>"))

        card_warnings = QFrame()
        card_warnings.setObjectName("SummaryCard")
        card_warnings.setStyleSheet("border-left: 3px solid #d29922;")
        lt3 = QVBoxLayout(card_warnings)
        lt3.addWidget(QLabel("<span style='color:#8b949e; font-size:10px; font-weight:bold;'>TOTAL WARNINGS</span>"))
        lt3.addWidget(QLabel(f"<span style='font-size:20px; font-weight:bold; color:#d29922;'>{self.report.total_warnings}</span>"))

        summary_layout.addWidget(card_traces)
        summary_layout.addWidget(card_violations)
        summary_layout.addWidget(card_warnings)
        layout.addLayout(summary_layout)

        # =================================================
        # FILTERS BAR
        # =================================================
        filters_container = QFrame()
        filters_container.setObjectName("ToolBlock")
        filters_layout = QHBoxLayout(filters_container)
        filters_layout.setContentsMargins(10, 6, 10, 6)
        filters_layout.setSpacing(10)

        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["ALL", "VIOLATION", "WARNING", "OK"])

        self.mutation_filter = QComboBox()
        mutations = sorted(set(r.mutation_name for r in self.report.trace_reports))
        self.mutation_filter.addItem("ALL")
        self.mutation_filter.addItems(mutations)

        self.severity_filter.currentTextChanged.connect(self._populate_table)
        self.mutation_filter.currentTextChanged.connect(self._populate_table)

        filters_layout.addWidget(QLabel("Filter Severity:"))
        filters_layout.addWidget(self.severity_filter)
        filters_layout.addWidget(QLabel("Filter Mutation Rule:"))
        filters_layout.addWidget(self.mutation_filter)
        filters_layout.addWidget(QLabel("<span style='color:#8b949e; font-size:11px; margin-left:10px;'>💡 Double-click a row to open full audit trail</span>"))
        filters_layout.addStretch()

        layout.addWidget(filters_container)

        # =================================================
        # DATA TABLE
        # =================================================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Trace Target ID",
            "Applied Mutation Engine",
            "Audit Status",
            "Violations Count",
            "Warnings Count"
        ])
        
        # Ajustes de comportamiento de tabla pro
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #1c2128; }")
        
        self.table.cellDoubleClicked.connect(self._open_trace_detail)
        layout.addWidget(self.table)

    def _populate_table(self):
        severity_filter = self.severity_filter.currentText()
        mutation_filter = self.mutation_filter.currentText()

        filtered = []
        for report in self.report.trace_reports:
            if severity_filter != "ALL" and report.severity != severity_filter:
                continue
            if mutation_filter != "ALL" and report.mutation_name != mutation_filter:
                continue
            filtered.append(report)

        self.filtered_reports = filtered
        self.table.setRowCount(len(filtered))

        for row, report in enumerate(filtered):
            violations = len(report.validator_result["violations"])
            warnings = len(report.validator_result["warnings"])

            # Trace ID (Centrado)
            item_id = QTableWidgetItem(str(report.trace_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            
            # Mutation Name
            item_mut = QTableWidgetItem(report.mutation_name)
            
            # Status Badge Dinámico
            item_sev = QTableWidgetItem(f" ● {report.severity}")
            if report.severity == "VIOLATION":
                item_sev.setForeground(Qt.GlobalColor.red)
            elif report.severity == "WARNING":
                item_sev.setForeground(Qt.GlobalColor.yellow)
            else:
                item_sev.setForeground(Qt.GlobalColor.green)
            font_bold = QFont()
            font_bold.setBold(True)
            item_sev.setFont(font_bold)

            # Violaciones (Centrado)
            item_v = QTableWidgetItem(str(violations))
            item_v.setTextAlignment(Qt.AlignCenter)
            if violations > 0:
                item_v.setForeground(Qt.GlobalColor.red)

            # Warnings (Centrado)
            item_w = QTableWidgetItem(str(warnings))
            item_w.setTextAlignment(Qt.AlignCenter)
            if warnings > 0:
                item_w.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, item_mut)
            self.table.setItem(row, 2, item_sev)
            self.table.setItem(row, 3, item_v)
            self.table.setItem(row, 4, item_w)

        self.table.resizeColumnsToContents()

    def _open_trace_detail(self, row, column):
        report = self.filtered_reports[row]
        dialog = TraceDetailDialog(report)
        dialog.exec()

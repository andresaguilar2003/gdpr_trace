import os

from PySide6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QFrame
)
from PySide6.QtGui import QFont, QColor, QPageLayout, QPageSize, QTextDocument
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter

class GdprRulesInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado inicial del idioma ('es' para Español, 'en' para Inglés)
        self.current_lang = 'es'
        
        self.resize(850, 750) 
        
        # Layout base de la ventana
        self.window_layout = QVBoxLayout(self)
        self.window_layout.setSpacing(14)
        self.window_layout.setContentsMargins(18, 18, 18, 18)
        
        # --- 🌐 BARRA SUPERIOR DINÁMICA DE IDIOMAS ---
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lang_btn = QPushButton("🇺🇸 Switch to English")
        self.lang_btn.setFixedWidth(160)
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                color: #58a6ff;
                border-color: #8b949e;
            }
        """)
        self.lang_btn.clicked.connect(self._toggle_language)
        lang_layout.addWidget(self.lang_btn)
        self.window_layout.addLayout(lang_layout)
        
        # --- BLOQUE INTRODUCTORIO DESTACADO ---
        self.intro_card = QFrame()
        self.intro_card.setObjectName("IntroCard")
        self.intro_card.setStyleSheet("""
            QFrame#IntroCard {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        card_layout = QVBoxLayout(self.intro_card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        
        self.intro_text = QLabel()
        self.intro_text.setWordWrap(True)
        self.intro_text.setStyleSheet("font-size: 13px; color: #c9d1d9; line-height: 1.4;")
        card_layout.addWidget(self.intro_text)
        self.window_layout.addWidget(self.intro_card)
        
        # --- ÁRBOL INTERACTIVO DE REGLAS ---
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #30363d;
                border-radius: 6px;
                background-color: #0d1117;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-bottom: 1px solid #21262d;
                color: #c9d1d9;
            }
            QTreeWidget::item:hover {
                background-color: #161b22;
            }
        """)
        self.window_layout.addWidget(self.tree)
        
        # --- ACCIONES ---
        self.actions_layout = QHBoxLayout()

        self.pdf_btn = QPushButton()
        self.pdf_btn.setFixedWidth(130)
        self.pdf_btn.setCursor(Qt.PointingHandCursor)
        self.pdf_btn.clicked.connect(self._export_to_pdf)
        self.actions_layout.addWidget(self.pdf_btn)

        self.actions_layout.addStretch()
        
        self.close_btn = QPushButton()
        self.close_btn.setFixedWidth(120)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.actions_layout.addWidget(self.close_btn)
        
        self.window_layout.addLayout(self.actions_layout)

        # Construir y rellenar textos iniciales basados en español
        self._update_ui_texts()

    def _toggle_language(self):
        """Conmutador de idioma que refresca los textos en tiempo real"""
        if self.current_lang == 'es':
            self.current_lang = 'en'
            self.lang_btn.setText("🇪🇸 Cambiar a Español")
        else:
            self.current_lang = 'es'
            self.lang_btn.setText("🇺🇸 Switch to English")
        
        self._update_ui_texts()

    def _update_ui_texts(self):
        """Actualiza dinámicamente todos los elementos textuales de la interfaz"""
        if self.current_lang == 'es':
            self.setWindowTitle("ℹ️ Metodología de Enriquecimiento y Reglas GDPR")
            self.pdf_btn.setText("📄 Exportar PDF")
            self.close_btn.setText("Entendido")
            
            self.intro_html_content = (
                "<span style='font-size: 14px; font-weight: bold; color: #58a6ff;'>Metodología de Auditoría</span><br/><br/>"
                "El proceso de <b>enriquecimiento de trazas</b> consiste en la inyección e inferencia de nuevos eventos "
                "de control contextuales dentro del dataset original. Estos eventos permiten reconstruir "
                "el flujo de operaciones vinculadas a la privacidad y el tratamiento de datos.<br/><br/>"
                "La conformidad normativa del modelo resultante se valida formalmente mediante la evaluación de restricciones "
                "escritas en <b>OCL (Object Constraint Language)</b>. A continuación se detalla la matriz de objetivos e "
                "invariantes que el sistema verifica rigurosamente en cada capítulo del RGPD:"
            )
        else:
            self.setWindowTitle("ℹ️ Enrichment Methodology and GDPR Rules")
            self.pdf_btn.setText("📄 Export PDF")
            self.close_btn.setText("Understood")
            
            self.intro_html_content = (
                "<span style='font-size: 14px; font-weight: bold; color: #58a6ff;'>Audit Methodology</span><br/><br/>"
                "The <b>trace enrichment</b> process consists of injecting and inferring new contextual "
                "control events into the original dataset. These events enable the reconstruction of "
                "the operational flow linked to privacy and data processing.<br/><br/>"
                "The regulatory compliance of the resulting model is formally validated by evaluating constraints "
                "written in <b>OCL (Object Constraint Language)</b>. The matrix of objectives and "
                "invariants that the system rigorously verifies for each GDPR chapter is detailed below:"
            )
            
        self.intro_text.setText(self.intro_html_content)
        self._populate_rules_tree()

    def _populate_rules_tree(self):
        self.tree.clear() # Limpiar el árbol antes de repoblarlo en otro idioma
        
        if self.current_lang == 'es':
            self.rules_data = [
                {
                    "capitulo": "Capítulo II — Principios (Artículos 5, 6, 7, 13)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Verificar la existencia de una base jurídica válida antes del tratamiento (Art. 5 y 6)",
                            "regla": "RULE: CASE_START_VERIFY_LEGAL_BASIS",
                            "ocl": "context Trace\n\ninv CASE_START_VERIFY_LEGAL_BASIS:\n    for all e in events where e.type = CASE_START:\n        exists g in events such that\n            g.name = verify_legal_basis AND\n            g.position = AFTER AND\n            g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Garantizar que el interesado recibe la información del tratamiento (Art. 13)",
                            "regla": "RULE: DATA_COLLECTION_NOTICE",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_NOTICE:\n    for all e where e.type = DATA_COLLECTION:\n        exists g where\n            g.name = privacy_notice_disclosed AND\n            g.position = AFTER AND\n            g.order >= e.order"
                        },
                        {
                            "titulo": "☑️ Validar el consentimiento explícito si es la base jurídica estipulada (Art. 6 y 7)",
                            "regla": "RULE: DATA_COLLECTION_CONSENT_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_CONSENT_REQUIRED:\n    if legal_basis = consent:\n        exists g where\n            g.name = check_consent AND\n            g.position = BEFORE AND\n            g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Asegurar la precedencia de la base jurídica frente a la recolección de datos (Art. 5 y 6)",
                            "regla": "RULE: DATA_COLLECTION_LEGAL_BASIS_FLOW",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_LEGAL_BASIS_FLOW:\n    for all e where e.type = DATA_COLLECTION:\n        exists s in events such that\n            s.type = CASE_START AND\n            s.order < e.order\n        and\n        exists g in events such that\n            g.name = 'verify_legal_basis' AND\n            g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Controlar la limitación de la finalidad y el registro formal de actividades (Art. 5.1.b y 30)",
                            "regla": "RULE: DATA_COLLECTION_PURPOSE_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_PURPOSE_REQUIRED:\n    for all e where e.type = DATA_COLLECTION:\n        exists g where\n            g.name = record_purpose"
                        }
                    ]
                },
                {
                    "capitulo": "Capítulo III — Derechos del Interesado (Artículos 12–23)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Autenticar formalmente la identidad del solicitante para evitar accesos no autorizados (Art. 12.2)",
                            "regla": "RULE: USER_RIGHT_IDENTITY_VERIFICATION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_IDENTITY_VERIFICATION:\n    for all e where e.type = USER_RIGHT_REQUEST:\n        exists g where g.name = verify_request_identity AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Asegurar la obligatoriedad de emitir una respuesta formal a toda solicitud de derechos (Art. 12, 15-18, 21)",
                            "regla": "RULE: USER_RIGHT_REQUEST_RESPONSE_REQUIRED",
                            "ocl": "context Trace\n\ninv USER_RIGHT_REQUEST_RESPONSE_REQUIRED:\n    for all e where e.type = USER_RIGHT_REQUEST:\n        exists g where g.name = respond_user_right AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Acceso: Proveer copia íntegra y segura de los datos bajo tratamiento tras autenticación (Art. 15)",
                            "regla": "RULE: USER_RIGHT_ACCESS_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_ACCESS_DATA_COPY:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = ACCESS:\n        exists g where g.name = provide_data_copy AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Rectificación: Actualizar registros primarios, propagar a réplicas y notificar a terceros (Art. 16 y 19)",
                            "regla": "RULE: USER_RIGHT_RECTIFICATION_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_RECTIFICATION_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = RECTIFICATION:\n        exists g1 where g1.name = update_primary_record and g1.order > e.order\n        and exists g2 where g2.name = propagate_rectification_to_replicas and g2.order > e.order\n        and exists g3 where g3.name = notify_data_rectification_to_recipients and g3.order > e.order\n        and exists g4 where g4.name = verify_rectification_consistency and g4.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Supresión ('Olvido'): Borrado total en base primaria, réplicas y comunicación de baja a terceros (Art. 17 y 19)",
                            "regla": "RULE: USER_RIGHT_ERASURE_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_ERASURE_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = ERASURE:\n        exists g1 where g1.name = erase_primary_record and g1.order > e.order\n        and exists g2 where g2.name = propagate_erasure_to_replicas and g2.order > e.order\n        and exists g3 where g3.name = notify_third_party_deletion and g3.order > e.order\n        and exists g4 where g4.name = verify_erasure_completion and g4.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho a la Limitación: Bloquear el tratamiento ordinario y restringir accesos marcando los datos (Art. 12 y 18)",
                            "regla": "RULE: USER_RIGHT_RESTRICTION_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_RESTRICTION_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = RESTRICTION:\n        exists g0 where g0.name = verify_request_identity and g0.order < e.order\n        and exists g1 where g1.name = verify_restriction_lift_conditions and g1.order < e.order\n        and exists g2 where g2.name = mark_data_as_restricted and g2.order > e.order\n        and exists g3 where g3.name = respond_user_right and g3.order > g2.order"
                        },
                        {
                            "titulo": "☑️ Derecho a la Portabilidad: Generar exportaciones estructuradas en formatos interoperables (Art. 20)",
                            "regla": "RULE: USER_RIGHT_PORTABILITY_FORMAT",
                            "ocl": "context Trace\n\ninv USER_RIGHT_PORTABILITY_FORMAT:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:\n        exists g where g.name = generate_interoperable_format AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho a la Portabilidad: Viabilizar la transmisión directa automatizada entre responsables (Art. 20.2)",
                            "regla": "RULE: USER_RIGHT_PORTABILITY_TRANSMISSION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_PORTABILITY_TRANSMISSION:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:\n        exists g where g.name = transmit_data_to_new_controller AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Oposición: Forzar el cese inmediato del flujo operacional asociado a la queja (Art. 21)",
                            "regla": "RULE: USER_RIGHT_OBJECTION_HALT",
                            "ocl": "context Trace\n\ninv USER_RIGHT_OBJECTION_HALT:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:\n        exists g where g.name = halt_processing_activities AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Oposición: Evaluar y justificar motivos legítimos imperiosos si se requiere denegar la queja (Art. 21.1)",
                            "regla": "RULE: USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:\n        exists g where g.name = verify_compelling_legitimate_grounds AND g.position = BEFORE"
                        },
                        {
                            "titulo": "☑️ Decisiones Automatizadas: Viabilizar la impugnación de fallos de IA y garantizar el derecho a intervención humana (Art. 22.3)",
                            "regla": "RULE: USER_RIGHT_AUTOMATED_DECISION_CONTEST",
                            "ocl": "context Trace\n\ninv USER_RIGHT_AUTOMATED_DECISION_CONTEST:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = AUTOMATED_DECISION_REVIEW:\n        exists g where g.name = contest_automated_decision AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Derecho de Información: Facilitar detalles explícitos sobre fines, identidad del DPO y bases legales (Art. 13 y 14)",
                            "regla": "RULE: USER_RIGHT_INFORMATION_TRANSPARENCY",
                            "ocl": "context Trace\n\ninv USER_RIGHT_INFORMATION_TRANSPARENCY:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = INFORMATION:\n        exists g where g.name = provide_transparency_details AND g.position = AFTER AND g.order > e.order"
                        }
                    ]
                },
                {
                    "capitulo": "Capítulo IV — Responsable y Encargado del Tratamiento (Artículos 24–43)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Exigir controles de verificación preventivos para la minimización de datos en el tratamiento (Art. 5.1.c y 25)",
                            "regla": "RULE: DATA_PROCESSING_MINIMISATION",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_MINIMISATION:\n    for all e where e.type = DATA_PROCESSING:\n        exists g where g.name = minimisation_check AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Imponer el cifrado de datos previo para mitigar riesgos en categorías no estándar (Art. 32)",
                            "regla": "RULE: DATA_PROCESSING_ENCRYPTION_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_ENCRYPTION_REQUIRED:\n    if data_category != STANDARD:\n        exists g where g.name = encryption_applied AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Garantizar la trazabilidad obligatoria y registro formal de actividades de tratamiento (Art. 5.2 y 30)",
                            "regla": "RULE: DATA_PROCESSING_LOG_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_LOG_REQUIRED:\n    for all e where e.type = DATA_PROCESSING:\n        exists g where g.name = log_processing_activity\n        OR\n        exists g where g.name = log_processing_activity AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Validar la existencia de controles de acceso específicos en categorías sensibles o de salud (Art. 9 y 32)",
                            "regla": "RULE: DATA_ACCESS_CONTROL_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_ACCESS_CONTROL_REQUIRED:\n    if data_category in {HEALTH, SPECIAL}:\n        exists g where g.name = access_control_check AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Verificar de forma preventiva los acuerdos formales con encargados del tratamiento de datos (Art. 28)",
                            "regla": "RULE: DATA_TRANSFER_THIRD_PARTY_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_THIRD_PARTY_REQUIRED:\n    if has_third_party_recipients = true:\n        exists g where g.name = check_third_party_agreement AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Asegurar la transparencia informando preventivamente sobre la lógica aplicada en decisiones IA (Art. 22 y 13.2.f)",
                            "regla": "RULE: AUTOMATED_DECISION_DISCLOSURE_REQUIRED",
                            "ocl": "context Trace\n\ninv AUTOMATED_DECISION_DISCLOSURE_REQUIRED:\n    for all e where e.type = AUTOMATED_DECISION:\n        exists g where g.name = automated_logic_disclosure AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Forzar el registro de la política de retención con anterioridad al borrado definitivo del dato (Art. 5.1.e)",
                            "regla": "RULE: DATA_DELETION_RETENTION_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_DELETION_RETENTION_REQUIRED:\n    for all e where e.type = DATA_DELETION:\n        exists g1 where g1.name = record_retention_period AND g1.order < e.order"
                        },
                        {
                            "titulo": "☑️ Asegurar la confirmación efectiva de la purga técnica tras una instrucción de supresión (Art. 17)",
                            "regla": "RULE: DATA_DELETION_ERASE_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_DELETION_ERASE_REQUIRED:\n    for all e where e.type = DATA_DELETION:\n        exists g where g.name = erase_data AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Verificar preventivamente el vencimiento de los plazos legales de conservación al cierre del caso (Art. 5.1.e)",
                            "regla": "RULE: CASE_END_RETENTION_VERIFY",
                            "ocl": "context Trace\n\ninv CASE_END_RETENTION_VERIFY:\n    for all e in events where e.type = CASE_END:\n        exists g in events such that g.name = 'retention_period_verify' AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Forzar la supresión técnica automatizada de los datos cuando expire el periodo de retención fijado (Art. 17 y 25)",
                            "regla": "RULE: CASE_END_ERASURE",
                            "ocl": "context Trace\n\ninv CASE_END_ERASURE:\n    for all e in events where e.type = CASE_END:\n        if not context.retention_period.oclIsUndefined() then\n            exists g in events such that g.name = 'confirm_data_erasure' AND g.position = BEFORE AND g.order < e.order\n        else\n            true\n        endif"
                        }
                    ]
                },
                {
                    "capitulo": "Capítulo V — Transferencias Internacionales (Artículos 44–50)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Validar y auditar la presencia de salvaguardas legales antes de transferir datos a terceros países (Art. 44 y 46)",
                            "regla": "RULE: DATA_TRANSFER_INTERNATIONAL_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_INTERNATIONAL_REQUIRED:\n    if international_transfer = \"third_country\":\n        exists g where g.name = verify_international_safeguard AND g.position = BEFORE AND g.order < e.order"
                        }
                    ]
                },
                {
                    "capitulo": "⚠️ Warnings y Señales de Cumplimiento No Críticas (Análisis de Eficiencia)",
                    "color": "#d4a727",
                    "objetivos": [
                        {
                            "titulo": "⚠️ Alerta: Detección de validación de consentimiento redundante cuando la base jurídica es distinta (Art. 6)",
                            "regla": "WARNING: DATA_COLLECTION_CONSENT_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_CONSENT_FORBIDDEN:\n    if legal_basis != consent:\n        not exists g where g.name = check_consent"
                        },
                        {
                            "titulo": "⚠️ Alerta: Aplicación ineficiente de cifrado de alta seguridad en categorías de datos estándares (Art. 32)",
                            "regla": "WARNING: DATA_PROCESSING_ENCRYPTION_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_ENCRYPTION_FORBIDDEN:\n    if data_category = STANDARD:\n        not exists g where g.name = encryption_applied"
                        },
                        {
                            "titulo": "⚠️ Alerta: Controles de acceso restrictivos detectados sobre categorías de datos comunes o no sensibles (Art. 32)",
                            "regla": "WARNING: DATA_ACCESS_CONTROL_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_ACCESS_CONTROL_FORBIDDEN:\n    if data_category not in {HEALTH, SPECIAL}:\n        not exists g where g.name = access_control_check"
                        },
                        {
                            "titulo": "⚠️ Alerta: Verificación innecesaria de contratos de encargo (DPA) en flujos sin cesión a terceros (Art. 28)",
                            "regla": "WARNING: DATA_TRANSFER_THIRD_PARTY_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_THIRD_PARTY_FORBIDDEN:\n    if has_third_party_recipients = false:\n        not exists g where g.name = check_third_party_agreement"
                        },
                        {
                            "titulo": "⚠️ Alerta: Auditoría de salvaguardas de transferencia ejecutada sobre flujos exclusivamente nacionales (Art. 44)",
                            "regla": "WARNING: DATA_TRANSFER_INTERNATIONAL_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_INTERNATIONAL_FORBIDDEN:\n    if international_transfer != \"third_country\":\n        not exists g where g.name = verify_international_safeguard"
                        }
                    ]
                }
            ]
        else:
            # Versión en Inglés mapeada exactamente igual
            self.rules_data = [
                {
                    "capitulo": "Chapter II — Principles (Articles 5, 6, 7, 13)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Verify the existence of a valid legal basis prior to processing (Art. 5 & 6)",
                            "regla": "RULE: CASE_START_VERIFY_LEGAL_BASIS",
                            "ocl": "context Trace\n\ninv CASE_START_VERIFY_LEGAL_BASIS:\n    for all e in events where e.type = CASE_START:\n        exists g in events such that\n            g.name = verify_legal_basis AND\n            g.position = AFTER AND\n            g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Ensure that the data subject receives the processing information statement (Art. 13)",
                            "regla": "RULE: DATA_COLLECTION_NOTICE",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_NOTICE:\n    for all e where e.type = DATA_COLLECTION:\n        exists g where\n            g.name = privacy_notice_disclosed AND\n            g.position = AFTER AND\n            g.order >= e.order"
                        },
                        {
                            "titulo": "☑️ Validate explicit consent if it is the mandated legal basis (Art. 6 & 7)",
                            "regla": "RULE: DATA_COLLECTION_CONSENT_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_CONSENT_REQUIRED:\n    if legal_basis = consent:\n        exists g where\n            g.name = check_consent AND\n            g.position = BEFORE AND\n            g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Ensure the precedence of the legal basis verification prior to data collection (Art. 5 & 6)",
                            "regla": "RULE: DATA_COLLECTION_LEGAL_BASIS_FLOW",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_LEGAL_BASIS_FLOW:\n    for all e where e.type = DATA_COLLECTION:\n        exists s in events such that\n            s.type = CASE_START AND\n            s.order < e.order\n        and\n        exists g in events such that\n            g.name = 'verify_legal_basis' AND\n            g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Control purpose limitation and enforce the formal log of processing activities (Art. 5.1.b & 30)",
                            "regla": "RULE: DATA_COLLECTION_PURPOSE_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_PURPOSE_REQUIRED:\n    for all e where e.type = DATA_COLLECTION:\n        exists g where\n            g.name = record_purpose"
                        }
                    ]
                },
                {
                    "capitulo": "Chapter III — Data Subject Rights (Articles 12–23)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Formally authenticate the identity of the requester to prevent unauthorized access (Art. 12.2)",
                            "regla": "RULE: USER_RIGHT_IDENTITY_VERIFICATION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_IDENTITY_VERIFICATION:\n    for all e where e.type = USER_RIGHT_REQUEST:\n        exists g where g.name = verify_request_identity AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Ensure the obligation to issue a formal response to all user right requests (Art. 12, 15-18, 21)",
                            "regla": "RULE: USER_RIGHT_REQUEST_RESPONSE_REQUIRED",
                            "ocl": "context Trace\n\ninv USER_RIGHT_REQUEST_RESPONSE_REQUIRED:\n    for all e where e.type = USER_RIGHT_REQUEST:\n        exists g where g.name = respond_user_right AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right of Access: Provide a full and secure copy of the processed data after authentication (Art. 15)",
                            "regla": "RULE: USER_RIGHT_ACCESS_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_ACCESS_DATA_COPY:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = ACCESS:\n        exists g where g.name = provide_data_copy AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Rectification: Update primary logs, propagate changes to replicas and notify third parties (Art. 16 & 19)",
                            "regla": "RULE: USER_RIGHT_RECTIFICATION_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_RECTIFICATION_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = RECTIFICATION:\n        exists g1 where g1.name = update_primary_record and g1.order > e.order\n        and exists g2 where g2.name = propagate_rectification_to_replicas and g2.order > e.order\n        and exists g3 where g3.name = notify_data_rectification_to_recipients and g3.order > e.order\n        and exists g4 where g4.name = verify_rectification_consistency and g4.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Erasure ('Forgotten'): Total erasure in primary, replicas, and cessation broadcast to third parties (Art. 17 & 19)",
                            "regla": "RULE: USER_RIGHT_ERASURE_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_ERASURE_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = ERASURE:\n        exists g1 where g1.name = erase_primary_record and g1.order > e.order\n        and exists g2 where g2.name = propagate_erasure_to_replicas and g2.order > e.order\n        and exists g3 where g3.name = notify_third_party_deletion and g3.order > e.order\n        and exists g4 where g4.name = verify_erasure_completion and g4.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Restriction: Halt standard operations and restrict access by tagging the records (Art. 12 & 18)",
                            "regla": "RULE: USER_RIGHT_RESTRICTION_COMPLIANCE",
                            "ocl": "context Trace\n\ninv USER_RIGHT_RESTRICTION_COMPLIANCE:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = RESTRICTION:\n        exists g0 where g0.name = verify_request_identity and g0.order < e.order\n        and exists g1 where g1.name = verify_restriction_lift_conditions and g1.order < e.order\n        and exists g2 where g2.name = mark_data_as_restricted and g2.order > e.order\n        and exists g3 where g3.name = respond_user_right and g3.order > g2.order"
                        },
                        {
                            "titulo": "☑️ Right to Portability: Generate structured exports into interoperable standard formats (Art. 20)",
                            "regla": "RULE: USER_RIGHT_PORTABILITY_FORMAT",
                            "ocl": "context Trace\n\ninv USER_RIGHT_PORTABILITY_FORMAT:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:\n        exists g where g.name = generate_interoperable_format AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Portability: Enable automated direct transmission from controller to controller (Art. 20.2)",
                            "regla": "RULE: USER_RIGHT_PORTABILITY_TRANSMISSION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_PORTABILITY_TRANSMISSION:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:\n        exists g where g.name = transmit_data_to_new_controller AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Object: Enforce an immediate halt of the operational flow linked to the objection request (Art. 21)",
                            "regla": "RULE: USER_RIGHT_OBJECTION_HALT",
                            "ocl": "context Trace\n\ninv USER_RIGHT_OBJECTION_HALT:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:\n        exists g where g.name = halt_processing_activities AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Object: Evaluate and justify compelling legitimate grounds if a denial is required (Art. 21.1)",
                            "regla": "RULE: USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION",
                            "ocl": "context Trace\n\ninv USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:\n        exists g where g.name = verify_compelling_legitimate_grounds AND g.position = BEFORE"
                        },
                        {
                            "titulo": "☑️ Automated Decisions: Enable the contesting of AI claims and guarantee human intervention rights (Art. 22.3)",
                            "regla": "RULE: USER_RIGHT_AUTOMATED_DECISION_CONTEST",
                            "ocl": "context Trace\n\ninv USER_RIGHT_AUTOMATED_DECISION_CONTEST:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = AUTOMATED_DECISION_REVIEW:\n        exists g where g.name = contest_automated_decision AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Right to Information: Provide explicit details on purposes, DPO identity, and legal claims (Art. 13 & 14)",
                            "regla": "RULE: USER_RIGHT_INFORMATION_TRANSPARENCY",
                            "ocl": "context Trace\n\ninv USER_RIGHT_INFORMATION_TRANSPARENCY:\n    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = INFORMATION:\n        exists g where g.name = provide_transparency_details AND g.position = AFTER AND g.order > e.order"
                        }
                    ]
                },
                {
                    "capitulo": "Chapter IV — Controller and Processor (Articles 24–43)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Require preventive verification controls for data minimisation during processing (Art. 5.1.c & 25)",
                            "regla": "RULE: DATA_PROCESSING_MINIMISATION",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_MINIMISATION:\n    for all e where e.type = DATA_PROCESSING:\n        exists g where g.name = minimisation_check AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Enforce preventive data encryption to mitigate risks in non-standard data types (Art. 32)",
                            "regla": "RULE: DATA_PROCESSING_ENCRYPTION_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_ENCRYPTION_REQUIRED:\n    if data_category != STANDARD:\n        exists g where g.name = encryption_applied AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Guarantee mandatory traceability and a formal log of processing activities (Art. 5.2 & 30)",
                            "regla": "RULE: DATA_PROCESSING_LOG_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_LOG_REQUIRED:\n    for all e where e.type = DATA_PROCESSING:\n        exists g where g.name = log_processing_activity\n        OR\n        exists g where g.name = log_processing_activity AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Validate the existence of role-based access controls for health or sensitive records (Art. 9 & 32)",
                            "regla": "RULE: DATA_ACCESS_CONTROL_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_ACCESS_CONTROL_REQUIRED:\n    if data_category in {HEALTH, SPECIAL}:\n        exists g where g.name = access_control_check AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Preventively verify formal Data Processing Agreements (DPA) with third-party processors (Art. 28)",
                            "regla": "RULE: DATA_TRANSFER_THIRD_PARTY_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_THIRD_PARTY_REQUIRED:\n    if has_third_party_recipients = true:\n        exists g where g.name = check_third_party_agreement AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Ensure transparency by preventively disclosing the logic applied in automated AI choices (Art. 22 & 13.2.f)",
                            "regla": "RULE: AUTOMATED_DECISION_DISCLOSURE_REQUIRED",
                            "ocl": "context Trace\n\ninv AUTOMATED_DECISION_DISCLOSURE_REQUIRED:\n    for all e where e.type = AUTOMATED_DECISION:\n        exists g where g.name = automated_logic_disclosure AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Force the recording of retention guidelines prior to the final technical data deletion (Art. 5.1.e)",
                            "regla": "RULE: DATA_DELETION_RETENTION_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_DELETION_RETENTION_REQUIRED:\n    for all e where e.type = DATA_DELETION:\n        exists g1 where g1.name = record_retention_period AND g1.order < e.order"
                        },
                        {
                            "titulo": "☑️ Ensure effective confirmation of technical wiping after a deletion prompt (Art. 17)",
                            "regla": "RULE: DATA_DELETION_ERASE_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_DELETION_ERASE_REQUIRED:\n    for all e where e.type = DATA_DELETION:\n        exists g where g.name = erase_data AND g.order > e.order"
                        },
                        {
                            "titulo": "☑️ Preventively audit the expiration of lawful storage terms at the closing of a case (Art. 5.1.e)",
                            "regla": "RULE: CASE_END_RETENTION_VERIFY",
                            "ocl": "context Trace\n\ninv CASE_END_RETENTION_VERIFY:\n    for all e in events where e.type = CASE_END:\n        exists g in events such that g.name = 'retention_period_verify' AND g.position = BEFORE AND g.order < e.order"
                        },
                        {
                            "titulo": "☑️ Force technical automated data erasure when the set retention framework expires (Art. 17 & 25)",
                            "regla": "RULE: CASE_END_ERASURE",
                            "ocl": "context Trace\n\ninv CASE_END_ERASURE:\n    for all e in events where e.type = CASE_END:\n        if not context.retention_period.oclIsUndefined() then\n            exists g in events such that g.name = 'confirm_data_erasure' AND g.position = BEFORE AND g.order < e.order\n        else\n            true\n        endif"
                        }
                    ]
                },
                {
                    "capitulo": "Chapter V — International Transfers (Articles 44–50)",
                    "color": "#58a6ff",
                    "objetivos": [
                        {
                            "titulo": "☑️ Validate and audit legal transfer safeguards before sending records to third countries (Art. 44 & 46)",
                            "regla": "RULE: DATA_TRANSFER_INTERNATIONAL_REQUIRED",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_INTERNATIONAL_REQUIRED:\n    if international_transfer = \"third_country\":\n        exists g where g.name = verify_international_safeguard AND g.position = BEFORE AND g.order < e.order"
                        }
                    ]
                },
                {
                    "capitulo": "⚠️ Warnings and Non-Critical Compliance Indicators (Efficiency Analysis)",
                    "color": "#d4a727",
                    "objetivos": [
                        {
                            "titulo": "⚠️ Warning: Redundant consent validation detected when another lawful basis is stated (Art. 6)",
                            "regla": "WARNING: DATA_COLLECTION_CONSENT_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_COLLECTION_CONSENT_FORBIDDEN:\n    if legal_basis != consent:\n        not exists g where g.name = check_consent"
                        },
                        {
                            "titulo": "⚠️ Warning: Inefficient application of high-security encryption over standard data classifications (Art. 32)",
                            "regla": "WARNING: DATA_PROCESSING_ENCRYPTION_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_PROCESSING_ENCRYPTION_FORBIDDEN:\n    if data_category = STANDARD:\n        not exists g where g.name = encryption_applied"
                        },
                        {
                            "titulo": "⚠️ Warning: Overly restrictive access controls deployed over non-sensitive or common data types (Art. 32)",
                            "regla": "WARNING: DATA_ACCESS_CONTROL_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_ACCESS_CONTROL_FORBIDDEN:\n    if data_category not in {HEALTH, SPECIAL}:\n        not exists g where g.name = access_control_check"
                        },
                        {
                            "titulo": "⚠️ Warning: Unnecessary verification of third-party contracts (DPA) in internal flows with no external routing (Art. 28)",
                            "regla": "WARNING: DATA_TRANSFER_THIRD_PARTY_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_THIRD_PARTY_FORBIDDEN:\n    if has_third_party_recipients = false:\n        not exists g where g.name = check_third_party_agreement"
                        },
                        {
                            "titulo": "⚠️ Warning: International transfer safeguard validation executed on strictly domestic operational paths (Art. 44)",
                            "regla": "WARNING: DATA_TRANSFER_INTERNATIONAL_FORBIDDEN",
                            "ocl": "context Trace\n\ninv DATA_TRANSFER_INTERNATIONAL_FORBIDDEN:\n    if international_transfer != \"third_country\":\n        not exists g where g.name = verify_international_safeguard"
                        }
                    ]
                }
            ]

        font_mono = QFont("Courier New", 10)
        font_mono.setStyleHint(QFont.Monospace)

        for cap in self.rules_data:
            cap_item = QTreeWidgetItem(self.tree)
            cap_item.setText(0, cap["capitulo"])
            cap_item.setFirstColumnSpanned(True)
            
            font_cap = QFont()
            font_cap.setBold(True)
            font_cap.setPointSize(11)
            cap_item.setFont(0, font_cap)
            cap_item.setForeground(0, QColor(cap["color"]))
            
            for obj in cap["objetivos"]:
                obj_item = QTreeWidgetItem(cap_item)
                obj_item.setText(0, obj["titulo"])
                obj_item.setFirstColumnSpanned(True)
                
                detail_item = QTreeWidgetItem(obj_item)
                
                technical_id_prefix = "⚙️ Identificador Técnico:" if self.current_lang == 'es' else "⚙️ Technical Identifier:"
                details_text = f"{technical_id_prefix} {obj['regla']}\n\n{obj['ocl']}"
                
                detail_item.setText(0, details_text)
                detail_item.setFont(0, font_mono)
                detail_item.setForeground(0, QColor("#8b949e"))
                detail_item.setFirstColumnSpanned(True)

    def _export_to_pdf(self):
        """Genera un archivo PDF traducido según el idioma activo."""
        dialog_title = "Guardar Reporte de Reglas GDPR" if self.current_lang == 'es' else "Save GDPR Rules Report"
        pdf_type = "Documento PDF (*.pdf)" if self.current_lang == 'es' else "PDF Document (*.pdf)"
        
        file_path, _ = QFileDialog.getSaveFileName(self, dialog_title, "", pdf_type)
        
        if not file_path:
            return
            
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"
            
        try:
            intro_clean = self.intro_html_content.replace("#58a6ff", "#0056b3").replace("#c9d1d9", "#333333")
            doc_title = "Matriz de Reglas y Conformidad GDPR (Auditoría)" if self.current_lang == 'es' else "GDPR Compliance Matrix and Rules (Audit)"
            
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #222222; margin: 15mm; line-height: 1.5; font-size: 11pt; }}
                    h1 {{ color: #0056b3; font-size: 18pt; border-bottom: 2px solid #0056b3; padding-bottom: 6px; margin-bottom: 15px; }}
                    .intro {{ background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 12px; margin-bottom: 20px; font-size: 10.5pt; color: #495057; }}
                    .capitulo {{ background-color: #0056b3; color: white; padding: 6px 10px; font-size: 11.5pt; font-weight: bold; border-radius: 4px; margin-top: 20px; margin-bottom: 10px; }}
                    .objetivo {{ font-size: 11pt; font-weight: bold; color: #111111; margin-top: 12px; margin-bottom: 4px; padding-left: 4px; }}
                    .regla {{ font-size: 9.5pt; font-weight: bold; color: #495057; margin-bottom: 4px; padding-left: 15px; }}
                    pre {{ background-color: #f1f3f5; border-left: 3px solid #6c757d; font-family: 'Courier New', Courier, monospace; font-size: 9.5pt; padding: 8px; margin: 4px 0 12px 15px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <h1>{doc_title}</h1>
                <div class="intro">
                    {intro_clean}
                </div>
            """
            
            for cap in self.rules_data:
                html += f'<div class="capitulo">{cap["capitulo"]}</div>'
                for obj in cap["objetivos"]:
                    html += f'<div class="objetivo">{obj["titulo"]}</div>'
                    technical_lbl = "⚙️ Identificador Técnico:" if self.current_lang == 'es' else "⚙️ Technical Identifier:"
                    html += f'<div class="regla">{technical_lbl} {obj["regla"]}</div>'
                    
                    ocl_formatted = obj["ocl"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html += f'<pre>{ocl_formatted}</pre>'
                    
            html += "</body></html>"
            
            document = QTextDocument()
            document.setHtml(html)
            
            printer = QPrinter(QPrinter.ScreenResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            
            page_size = QPageSize(QPageSize.PageSizeId.A4)
            
            from PySide6.QtCore import QMarginsF
            margins = QMarginsF(10.0, 10.0, 10.0, 10.0)
            
            page_layout = QPageLayout(
                page_size,
                QPageLayout.Orientation.Portrait,
                margins,
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
            document.print_(printer)
            
            success_title = "Exportación Exitosa" if self.current_lang == 'es' else "Export Successful"
            success_msg = f"El reporte técnico ha sido exportado correctamente en:\n\n{os.path.basename(file_path)}" if self.current_lang == 'es' else f"The technical report has been exported successfully to:\n\n{os.path.basename(file_path)}"
            
            QMessageBox.information(self, success_title, success_msg)
            
        except Exception as e:
            err_title = "Error de Exportación" if self.current_lang == 'es' else "Export Error"
            err_msg = f"No se pudo generar el archivo PDF debido al siguiente error:\n\n{str(e)}" if self.current_lang == 'es' else f"Could not generate the PDF file due to the following error:\n\n{str(e)}"
            QMessageBox.critical(self, err_title, err_msg)

import copy
from pathlib import Path

import pm4py

from app.mutations.registry.mutation_registry import MUTATION_REGISTRY
from app.mutations.services.mutation_engine import MutationEngine
from app.services.ai.t5.t5_client import T5Client
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog
from app.services.ai.t5.validators.ai_gdpr_validator import AIGDPRValidator
from app.services.ai.t5.validators.ai_gdpr_impact_validator import AIGDPRImpactValidator
from app.services.pm4py_log_converter import traces_to_pm4py_log
from app.services.trace_context_inferer import TraceContextInferer, GDPRContextNormalizer
from app.validation.validators.gdpr_enrichment_validator import GDPREnrichmentValidator
from app.ui.maps.graph_builder import build_graph
from app.analytics.process_metrics import ProcessMetrics
from app.services.gdpr_log_enricher import GDPRLogEnricher
from app.services.trace_builder import build_traces_from_pm4py_log
from app.models.context import Context
from app.specifications.data_categories import DataCategory


class _DeterministicValidatorAdapter:

    @staticmethod
    def validate(trace):
        result = GDPREnrichmentValidator.validate(trace)
        result["validation_mode"] = "deterministic"

        return result


class _AIValidatorAdapter:

    def __init__(self, ai_validator, fallback_to_deterministic=True):
        self.ai_validator = ai_validator
        self.fallback_to_deterministic = fallback_to_deterministic

    def validate(self, trace):
        deterministic_result = GDPREnrichmentValidator.validate(trace)
        deterministic_violations = deterministic_result.get("violations", [])
        deterministic_warnings = deterministic_result.get("warnings", [])
        rule_label = self._primary_rule_label(
            deterministic_violations,
            deterministic_warnings,
        )

        try:
            result = self.ai_validator.validate(trace, rule_label=rule_label)
        except TypeError:
            result = self.ai_validator.validate(trace)

        result["validation_mode"] = "ai"
        result["rule_evaluated"] = rule_label

        if result.get("impact") == "1_VIOLATION" and deterministic_violations:
            result["violations"] = list(deterministic_violations)

        if result.get("impact") == "2_WARNING" and deterministic_warnings:
            result["warnings"] = list(deterministic_warnings)

        result["violations"] = self._complete_issues(
            result.get("violations", []),
            issue_type="violation",
            deterministic_issues=deterministic_violations
        )
        result["warnings"] = self._complete_issues(
            result.get("warnings", []),
            issue_type="warning",
            deterministic_issues=deterministic_warnings
        )
        result["deterministic_reference"] = deterministic_result

        return result

    @staticmethod
    def _primary_rule_label(violations, warnings):
        for issue in list(violations or []) + list(warnings or []):
            if issue.get("rule"):
                return issue["rule"]

        return "COMPLIANCE_CHECK"

    def _complete_issues(self, issues, issue_type, deterministic_issues=None):
        deterministic_issues = deterministic_issues or []

        completed = []

        for issue in issues:
            completed.append(
                ValidationRuleCatalog.enrich_issue(
                    issue,
                    issue_type=issue_type
                )
            )

        if (
            self.fallback_to_deterministic
            and deterministic_issues
            and (
                not completed
                or self._issue_set(completed) != self._issue_set(deterministic_issues)
            )
        ):
            return list(deterministic_issues)

        return completed

    @staticmethod
    def _issue_set(issues):
        return {
            (
                issue.get("rule"),
                issue.get("event")
            )
            for issue in issues
        }


class _DualValidatorAdapter:

    def __init__(self, ai_validator):
        self.ai_adapter = _AIValidatorAdapter(
            ai_validator,
            fallback_to_deterministic=False
        )

    def validate(self, trace):
        deterministic_result = GDPREnrichmentValidator.validate(trace)
        ai_result = self.ai_adapter.validate(trace)

        deterministic_violations = deterministic_result.get("violations", [])
        deterministic_warnings = deterministic_result.get("warnings", [])
        ai_violations = ai_result.get("violations", [])
        ai_warnings = ai_result.get("warnings", [])

        deterministic_valid = len(deterministic_violations) == 0
        ai_valid = len(ai_violations) == 0

        agreement = (
            deterministic_valid == ai_valid
            and self._issue_set(deterministic_violations) == self._issue_set(ai_violations)
            and self._issue_set(deterministic_warnings) == self._issue_set(ai_warnings)
        )

        result = {
            "validation_mode": "both",
            "violations": list(deterministic_violations),
            "warnings": list(deterministic_warnings),
            "deterministic_result": deterministic_result,
            "ai_result": ai_result,
            "agrees_with_ai": agreement
        }

        if not agreement:
            result["warnings"].append({
                "rule": "AI_DETERMINISTIC_MISMATCH",
                "event": "trace",
                "message": "T5 validation does not match the deterministic validator for this mutated trace.",
                "recommendation": "Inspect deterministic_result and ai_result in the trace detail panel and add more training examples for the missed rule pattern."
            })

        return result

    @staticmethod
    def _issue_set(issues):
        return {
            (
                issue.get("rule"),
                issue.get("event")
            )
            for issue in issues
        }


class LogController:

    def __init__(self):
        self.gdpr_engine = GDPRLogEnricher()
        self._ai_validator = None

        self.mutation_engine = MutationEngine(
            GDPREnrichmentValidator
        )

        self._current_graph = None
        self._current_metrics = None

    def _load_event_log(self, path):

        log = pm4py.read_xes(path)

        # Si PM4PY devuelve DataFrame lo convertimos
        if hasattr(log, "columns"):

            log = pm4py.convert_to_event_log(log)

        return log

    # ------------------------------------

    def process_log(self, path):

        log = self._load_event_log(path)

        graph = build_graph(log, include_log_gdpr=False, include_case_gdpr=False)

        metrics = ProcessMetrics.compute(log)

        self._current_graph = graph
        self._current_metrics = metrics

        return graph, metrics

    # ------------------------------------

    def create_gdpr_compliant_log(self, file_path):

        log = self._load_event_log(file_path)

        traces = build_traces_from_pm4py_log(log)

        dataset_context = TraceContextInferer.infer_dataset_context(traces)

        strict_context = GDPRContextNormalizer.normalize(
            copy.deepcopy(dataset_context)
        )

        enriched_traces = self.gdpr_engine.enrich_log(
            traces,
            dataset_context=dataset_context
        )

        enriched_log = traces_to_pm4py_log(enriched_traces,context=strict_context)

        self._last_enriched_log = enriched_log
        self._last_enriched_traces = enriched_traces
        self._last_context = strict_context
        self._last_activity_typing = self.gdpr_engine.last_activity_map

        graph = build_graph(
            enriched_log,
            include_log_gdpr=True,
            include_case_gdpr=True,
            context=dataset_context
        )

        self._current_graph = graph
        self._current_metrics = ProcessMetrics.compute(enriched_log)
        return graph

    def validate_enriched_traces_with_ai(self):

        if not hasattr(self, "_last_enriched_traces"):
            raise ValueError("No GDPR traces available")

        ai_validator = self._get_ai_validator()
        traces = copy.deepcopy(self._last_enriched_traces)

        if hasattr(self, "_last_context") and self._last_context is not None:
            for trace in traces:
                trace.context = copy.deepcopy(self._last_context)

        results = []

        for trace in traces:
            ai_result = ai_validator.validate(trace)
            deterministic_result = GDPREnrichmentValidator.validate(trace)

            deterministic_is_valid = (
                len(deterministic_result.get("violations", [])) == 0
            )

            ai_issue_set = self._issue_set(ai_result.get("violations", []))
            ai_warning_set = self._issue_set(ai_result.get("warnings", []))
            deterministic_issue_set = self._issue_set(
                deterministic_result.get("violations", [])
            )
            deterministic_warning_set = self._issue_set(
                deterministic_result.get("warnings", [])
            )

            results.append({
                "trace_id": trace.trace_id,
                "is_valid": ai_result.get("isValid", False),
                "violations": ai_result.get("violations", []),
                "warnings": ai_result.get("warnings", []),
                "raw_response": ai_result.get("rawResponse", ""),
                "parse_error": ai_result.get("parseError"),
                "deterministic_is_valid": deterministic_is_valid,
                "deterministic_violations": deterministic_result.get(
                    "violations",
                    []
                ),
                "deterministic_warnings": deterministic_result.get(
                    "warnings",
                    []
                ),
                "agrees_with_deterministic": (
                    ai_result.get("isValid", False) == deterministic_is_valid
                    and ai_issue_set == deterministic_issue_set
                    and ai_warning_set == deterministic_warning_set
                )
            })

        return results

    def _get_ai_validator(self):
        if self._ai_validator is not None:
            return self._ai_validator

        dsl_model_path = Path("app/services/ai/t5/models/gdpr_t5_impact_dsl")
        model_path = Path("app/services/ai/t5/models/gdpr_t5_validator")

        if dsl_model_path.exists():
            llm = T5Client(str(dsl_model_path))
            self._ai_validator = AIGDPRImpactValidator(llm)
            return self._ai_validator

        if model_path.exists():
            llm = T5Client(str(model_path))
        else:
            llm = T5Client("t5-small")

        self._ai_validator = AIGDPRValidator(llm)

        return self._ai_validator

    @staticmethod
    def _issue_set(issues):
        return {
            (
                issue.get("rule"),
                issue.get("event")
            )
            for issue in issues
        }
    

    def get_last_enriched_log(self):

        if not hasattr(self, "_last_enriched_log"):
            raise ValueError("No enriched log available")

        return self._last_enriched_log
    
    def export_gdpr_log(self, output_path):

        if not hasattr(self, "_last_enriched_log"):
            raise ValueError("No enriched log available")

        pm4py.write_xes(self._last_enriched_log, output_path)


    def apply_mutations(self, mutation_configs, validation_mode="deterministic"):

        if not hasattr(self, "_last_enriched_traces"):
            raise ValueError("No GDPR traces available")

        # 1. Hacemos la copia profunda inicial de las trazas enriquecidas
        traces = copy.deepcopy(
            self._last_enriched_traces
        )

        # =====================================================
        # 🌟 NUEVO: INYECTAR EL CONTEXTO EN LAS TRAZAS PARA EL VALIDADOR
        # =====================================================
        # Antes de procesar el plan y enviarlo al engine, aseguramos que cada 
        # traza individual tenga guardado su propio contexto. Así, cuando el engine 
        # llame a 'GDPREnrichmentValidator.validate(mutated_trace)', la propiedad 
        # 'trace.context.legal_basis' existirá con su valor real (ej: "consent").
        if hasattr(self, "_last_context") and self._last_context is not None:
            for t in traces:
                t.context = copy.deepcopy(self._last_context)

        # =====================================================
        # BUILD MUTATION PLAN
        # =====================================================

        class RuntimeMutationPlan:

            def __init__(self):
                self.mapping = {}

            def add(self, trace_id, mutation):

                if trace_id not in self.mapping:
                    self.mapping[trace_id] = []

                self.mapping[trace_id].append(
                    mutation
                )

            def get_mutations_for_trace(self, trace_id):
                return self.mapping.get(trace_id, [])

        plan = RuntimeMutationPlan()

        # =====================================================
        # CREATE MUTATIONS
        # =====================================================

        for config in mutation_configs:

            mutation_info = MUTATION_REGISTRY[
                config["mutation"]
            ]

            mutation = mutation_info[
                "factory"
            ]()

            start = config["start"]
            end = config["end"]

            for idx in range(start, end + 1):

                if idx >= len(traces):
                    continue

                trace_id = traces[idx].trace_id

                plan.add(trace_id, mutation)

        # =====================================================
        # APPLY
        # =====================================================

        validator = self._build_mutation_validator(validation_mode)
        mutation_engine = MutationEngine(validator)

        mutated_traces, report = (
            mutation_engine.apply_mutations(
                traces,
                plan
            )
        )
        report.validation_mode = validation_mode

        # =====================================================
        # BUILD LOG
        # =====================================================

        mutated_log = traces_to_pm4py_log(
            mutated_traces,
            context=self._last_context
        )
        
        self._last_mutated_log = mutated_log
        
        graph = build_graph(
            mutated_log,
            include_log_gdpr=True,
            include_case_gdpr=True,
            context=self._last_context
        )

        return graph, report

    def _build_mutation_validator(self, validation_mode):
        normalized_mode = (validation_mode or "deterministic").lower()

        if normalized_mode == "ai":
            return _AIValidatorAdapter(self._get_ai_validator())

        if normalized_mode == "both":
            return _DualValidatorAdapter(self._get_ai_validator())

        return _DeterministicValidatorAdapter()

    

    def export_mutated_log(self, output_path):

        if not hasattr(self, "_last_mutated_log"):
            raise ValueError(
                "No mutated log available"
            )

        pm4py.write_xes(
            self._last_mutated_log,
            output_path
        )

    # =====================================================
    # UI SUPPORT
    # =====================================================

    def get_mutations_by_category(self):

        result = {}

        for mutation_name, info in MUTATION_REGISTRY.items():

            category = info["category"].value

            if category not in result:
                result[category] = []

            result[category].append(
                mutation_name
            )

        return result
    
    def get_total_gdpr_traces(self):

        if not hasattr(self, "_last_enriched_traces"):
            return 0

        return len(self._last_enriched_traces)

    def get_last_activity_typing(self):
        activity_map = getattr(self, "_last_activity_typing", {})

        rows = []

        for activity_name, info in sorted(activity_map.items()):
            activity_type = info.get("activity_type")
            user_right_type = info.get("user_right_type")

            if hasattr(activity_type, "name"):
                activity_type = activity_type.name

            if hasattr(user_right_type, "name"):
                user_right_type = user_right_type.name

            rows.append({
                "activity": activity_name,
                "activity_type": activity_type or "OTHER",
                "user_right_type": user_right_type
            })

        return rows
    
    def get_current_graph(self):
        return self._current_graph

    # 🌟 NUEVO: Permite extraer métricas específicas de rendimiento de un nodo clicado en la UI
    def get_node_performance_metrics(self, node_id):
        """
        Busca si existen métricas avanzadas (tiempos de servicio, esperas) 
        asociadas a esta actividad específica en el último cálculo.
        """
        # 1. Validar que tengamos métricas y que sea un diccionario estructurado
        if not self._current_metrics or not isinstance(self._current_metrics, dict):
            return {}
        
        # 2. Extraer de manera segura el contenedor de actividades
        activities = self._current_metrics.get("activities", {})
        
        # 3. Validar que 'activities' sea un diccionario antes de buscar el node_id
        if isinstance(activities, dict):
            return activities.get(node_id, {})
            
        # Si 'activities' era otra cosa (ej. un contador entero), devolvemos vacío de forma segura
        return {}

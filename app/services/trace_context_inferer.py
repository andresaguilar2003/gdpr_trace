import json
import re
from collections import Counter

from app.models.context import Context
from app.services.ai.roberta_trace_context_inferer import RobertaTraceContextInferer
from app.specifications.data_categories import DataCategory


class TraceContextInferer:

    @staticmethod
    def _extract_json(text):

        if not text:
            return "{}"

        start = text.find("{")

        if start == -1:
            return "{}"

        brace_count = 0

        for i in range(start, len(text)):

            if text[i] == "{":
                brace_count += 1

            elif text[i] == "}":
                brace_count -= 1

                if brace_count == 0:
                    return text[start:i+1]

        # fallback:
        partial = text[start:]

        # intentar cerrar json truncado
        if partial.count("{") > partial.count("}"):
            partial += "}"

        return partial
    
    @staticmethod
    def _clean_llm_json(text):

        if not text:
            return "{}"

        # eliminar comentarios //
        text = re.sub(r"//.*", "", text)

        # eliminar comentarios tipo /* */
        text = re.sub(r"/\*[\s\S]*?\*/", "", text)

        # eliminar trailing commas
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        # =====================================================
        # ELIMINAR LÍNEAS SUELTAS INVÁLIDAS
        # =====================================================

        lines = text.splitlines()

        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            # eliminar líneas basura tipo:
            # 0,
            # 1,
            # true,
            # false,
            # etc.
            if re.fullmatch(r"[0-9]+,?", stripped):
                continue

            cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)

        # =====================================================
        # ELIMINAR COMAS DUPLICADAS
        # =====================================================

        text = re.sub(r",\s*,", ",", text)

        # =====================================================
        # CERRAR JSON TRUNCADO
        # =====================================================

        open_braces = text.count("{")
        close_braces = text.count("}")

        if close_braces < open_braces:
            text += "}" * (open_braces - close_braces)

        return text

    # ------------------------------------------------
    # DATASET CONTEXT INFERENCE
    # ------------------------------------------------

    @staticmethod
    def infer_dataset_context(traces):
        try:
            return RobertaTraceContextInferer.infer_dataset_context(traces)
        except Exception as exc:
            print("RoBERTa context inference error")
            print(exc)
            return Context()

    @staticmethod
    def infer_dataset_context_with_phi3(traces):

        activity_counter = Counter()
        attributes = Counter()

        for trace in traces:

            for event in trace.events:

                activity_counter[event.name] += 1

                if hasattr(event, "attributes") and event.attributes:

                    for k in event.attributes.keys():
                        attributes[k] += 1

        activities = list(activity_counter.keys())
        attributes_list = list(attributes.keys())

        top_activities = activity_counter.most_common(20)
        top_attributes = attributes.most_common(20)

        prompt = f"""
You are an expert in GDPR and business process analysis.

Infer the GDPR processing context of a dataset of event log traces.

The dataset may come from healthcare, banking, education,
government, e-commerce or any other domain.

Dataset information:

Activities observed:
{activities}

Most frequent activities:
{top_activities}

Attributes observed:
{attributes_list}

Most frequent attributes:
{top_attributes}

DATA CATEGORY TYPES:

STANDARD
SPECIAL
HEALTH
BIOMETRIC
GENETIC
CHILDREN
VULNERABLE
PROFILING
INTERNATIONAL_TRANSFER
RESEARCH

Return ONLY JSON.

JSON schema:

{{
"purpose": "",
"legal_basis": "",
"data_category": "standard",
"data_subject_type": "",
"processing_operation": "",
"retention_period": "",
"processing_domain": "",
"has_third_party_recipients": false,
"international_transfer": "none",
"transfer_safeguard": "none",
"consent_status": "not_needed"
}}
"""

        from app.services.llm_client import LLMClient

        response = LLMClient.ask(prompt)

        response = TraceContextInferer._extract_json(response)

        response = TraceContextInferer._clean_llm_json(
            response
        )

        try:
            data = json.loads(response)

        except Exception:

            print("Context inference JSON error")
            print(response)

            return Context()

        category_raw = str(
            data.get("data_category", "standard")
        ).strip().upper()

        # =====================================================
        # DIRECT ENUM MAPPING
        # =====================================================

        direct_mapping = {

            "STANDARD": DataCategory.STANDARD,

            "SPECIAL": DataCategory.SPECIAL,
            "SPECIAL_CATEGORIES": DataCategory.SPECIAL,

            "HEALTH": DataCategory.HEALTH,

            "BIOMETRIC": DataCategory.BIOMETRIC,

            "GENETIC": DataCategory.GENETIC,

            "CHILDREN": DataCategory.CHILDREN,

            "VULNERABLE": DataCategory.VULNERABLE,
            "VULNERABLE_INDIVIDUALS": DataCategory.VULNERABLE,

            "PROFILING": DataCategory.PROFILING,
            "AUTOMATED_DECISION_PROFILING": DataCategory.PROFILING,

            "INTERNATIONAL_TRANSFER": DataCategory.INTERNATIONAL_TRANSFER,

            "RESEARCH": DataCategory.RESEARCH,
            "RESEARCH_STATISTICAL": DataCategory.RESEARCH,
        }

        category_enum = direct_mapping.get(
            category_raw,
            DataCategory.STANDARD
        )

        # =====================================================
        # SEMANTIC OVERRIDE USING FULL CONTEXT
        # =====================================================

        semantic_text = " ".join([

            str(data.get("data_category", "")),
            str(data.get("purpose", "")),
            str(data.get("processing_operation", "")),
            str(data.get("processing_domain", "")),
            str(data.get("data_subject_type", "")),
            str(data.get("legal_basis", ""))

        ]).lower()

        # -----------------------------------------------------
        # Override STANDARD if stronger evidence exists
        # -----------------------------------------------------

        if category_enum == DataCategory.STANDARD:

            if any(k in semantic_text for k in [
                "health",
                "medical",
                "patient",
                "hospital",
                "clinical",
                "sepsis",
                "icu",
                "emergency room"
            ]):
                category_enum = DataCategory.HEALTH

            elif any(k in semantic_text for k in [
                "biometric",
                "fingerprint",
                "iris",
                "face recognition",
                "voice recognition"
            ]):
                category_enum = DataCategory.BIOMETRIC

            elif any(k in semantic_text for k in [
                "genetic",
                "dna",
                "genome"
            ]):
                category_enum = DataCategory.GENETIC

            elif any(k in semantic_text for k in [
                "children",
                "minor",
                "pediatric"
            ]):
                category_enum = DataCategory.CHILDREN

            elif any(k in semantic_text for k in [
                "profiling",
                "fraud scoring",
                "credit scoring",
                "automated decision"
            ]):
                category_enum = DataCategory.PROFILING

            elif any(k in semantic_text for k in [
                "religion",
                "political opinion",
                "sexual orientation"
            ]):
                category_enum = DataCategory.SPECIAL

            elif any(k in semantic_text for k in [
                "vulnerable",
                "elderly",
                "asylum"
            ]):
                category_enum = DataCategory.VULNERABLE

            elif any(k in semantic_text for k in [
                "research",
                "statistical"
            ]):
                category_enum = DataCategory.RESEARCH

            elif any(k in semantic_text for k in [
                "international transfer",
                "cross-border",
                "third country"
            ]):
                category_enum = DataCategory.INTERNATIONAL_TRANSFER

            else:
                category_enum = DataCategory.STANDARD


        context = Context(

            purpose=data.get("purpose"),

            legal_basis=data.get("legal_basis"),

            data_category=category_enum,

            data_subject_type=data.get("data_subject_type"),

            processing_operation=data.get("processing_operation"),

            retention_period=data.get("retention_period"),

            processing_domain=data.get("processing_domain"),

            has_third_party_recipients=data.get(
                "has_third_party_recipients",
                False
            ),

            international_transfer=data.get(
                "international_transfer",
                "none"
            ),

            transfer_safeguard=data.get(
                "transfer_safeguard",
                "none"
            ),

            consent_status=data.get(
                "consent_status",
                "not_needed"
            ),
        )

        return context
    
class GDPRContextNormalizer:

    LEGAL_BASES = {
        "consent",
        "contract",
        "legal_obligation"
    }

    @staticmethod
    def normalize(context):

        # -------------------------
        # LEGAL BASIS
        # -------------------------

        lb = (context.legal_basis or "").lower()

        if "consent" in lb:
            context.legal_basis = "consent"

        elif "contract" in lb:
            context.legal_basis = "contract"

        elif (
            "legal obligation" in lb
            or "legal_obligation" in lb
        ):
            context.legal_basis = "legal_obligation"

        else:
            context.legal_basis = "consent"

        # -------------------------
        # INTERNATIONAL TRANSFER
        # -------------------------

        transfer = (
            context.international_transfer or ""
        ).lower()

        if (
            "third" in transfer
            or "outside eu" in transfer
            or "cross-border" in transfer
        ):
            context.international_transfer = "third_country"

        else:
            context.international_transfer = "none"

        # -------------------------
        # RETENTION PERIOD
        # -------------------------

        retention = (context.retention_period or "").lower()

        if not retention:

            context.retention_period = None

        elif any(k in retention for k in [
            "no retention",
            "not retained",
            "none"
        ]):

            context.retention_period = "none"

        elif any(k in retention for k in [
            "until request",
            "erase request",
            "right to erasure",
            "article 17"
        ]):

            context.retention_period = "until_request"

        elif any(k in retention for k in [
            "required by law",
            "legal requirement",
            "regulation",
            "compliance",
            "healthcare regulations"
        ]):

            context.retention_period = "legal_requirement"

        elif any(k in retention for k in [
            "6 months",
            "12 months",
            "1 year",
            "2 years",
            "fixed period"
        ]):

            context.retention_period = "fixed_period"

        elif any(k in retention for k in [
            "as long as necessary",
            "necessary for the purpose",
            "until no longer needed"
        ]):

            context.retention_period = "indefinite"

        else:

            context.retention_period = "indefinite"

        return context

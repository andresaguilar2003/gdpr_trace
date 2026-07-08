from collections import Counter

from app.models.context import Context
from app.services.ai.roberta_client import RobertaClient
from app.specifications.data_categories import DataCategory


class RobertaTraceContextInferer:

    DOMAIN_LABELS = [
        "healthcare",
        "banking",
        "education",
        "government",
        "e-commerce",
        "human resources",
        "logistics",
        "generic business process"
    ]

    PURPOSE_LABELS = [
        "medical treatment",
        "customer service",
        "contract execution",
        "legal compliance",
        "research",
        "fraud prevention",
        "service delivery",
        "administrative case management"
    ]

    LEGAL_BASIS_LABELS = [
        "consent",
        "contract",
        "legal obligation"
    ]

    DATA_CATEGORY_LABELS = [
        "standard personal data",
        "special category personal data",
        "health data",
        "biometric data",
        "genetic data",
        "children data",
        "vulnerable individuals data",
        "profiling data",
        "international transfer data",
        "research data"
    ]

    CATEGORY_MAP = {
        "standard personal data": DataCategory.STANDARD,
        "special category personal data": DataCategory.SPECIAL,
        "health data": DataCategory.HEALTH,
        "biometric data": DataCategory.BIOMETRIC,
        "genetic data": DataCategory.GENETIC,
        "children data": DataCategory.CHILDREN,
        "vulnerable individuals data": DataCategory.VULNERABLE,
        "profiling data": DataCategory.PROFILING,
        "international transfer data": DataCategory.INTERNATIONAL_TRANSFER,
        "research data": DataCategory.RESEARCH
    }

    @classmethod
    def infer_dataset_context(cls, traces):
        summary = cls._build_summary(traces)
        summary_text = summary["text"]
        lower_text = summary_text.lower()

        domain = cls._classify(
            summary_text,
            cls.DOMAIN_LABELS,
            "This event log belongs to the {} domain."
        )

        purpose = cls._classify(
            summary_text,
            cls.PURPOSE_LABELS,
            "The processing purpose is {}."
        )

        legal_basis = cls._infer_legal_basis(lower_text)
        data_category = cls._infer_data_category(summary_text, lower_text)

        return Context(
            purpose=purpose,
            legal_basis=legal_basis,
            data_category=data_category,
            data_subject_type=cls._infer_data_subject_type(lower_text),
            processing_operation=purpose,
            retention_period=cls._infer_retention_period(lower_text),
            processing_domain=domain,
            has_third_party_recipients=cls._has_third_party_recipients(lower_text),
            international_transfer=cls._infer_international_transfer(lower_text),
            transfer_safeguard=cls._infer_transfer_safeguard(lower_text),
            consent_status="required" if legal_basis == "consent" else "not_needed"
        )

    @staticmethod
    def _build_summary(traces):
        activity_counter = Counter()
        attribute_counter = Counter()

        for trace in traces:
            for event in trace.events:
                activity_counter[event.name] += 1

                if hasattr(event, "attributes") and event.attributes:
                    for key in event.attributes.keys():
                        attribute_counter[key] += 1

        activities = [name for name, _ in activity_counter.most_common(40)]
        attributes = [name for name, _ in attribute_counter.most_common(40)]

        text = (
            "Activities: "
            + ", ".join(activities)
            + ". Attributes: "
            + ", ".join(attributes)
            + "."
        )

        return {
            "activities": activities,
            "attributes": attributes,
            "text": text
        }

    @staticmethod
    def _classify(text, labels, hypothesis_template):
        label, _ = RobertaClient.classify(
            text,
            labels,
            hypothesis_template=hypothesis_template
        )

        return label

    @classmethod
    def _infer_data_category(cls, summary_text, lower_text):
        keyword_category = cls._keyword_data_category(lower_text)

        if keyword_category is not None:
            return keyword_category

        label = cls._classify(
            summary_text,
            cls.DATA_CATEGORY_LABELS,
            "The data category is {}."
        )

        return cls.CATEGORY_MAP.get(label, DataCategory.STANDARD)

    @staticmethod
    def _keyword_data_category(lower_text):
        if any(word in lower_text for word in [
            "sepsis",
            "patient",
            "hospital",
            "triage",
            "diagnosis",
            "leucocytes",
            "crp",
            "lacticacid",
            "medical",
            "health"
        ]):
            return DataCategory.HEALTH

        if any(word in lower_text for word in [
            "fingerprint",
            "biometric",
            "iris",
            "face recognition"
        ]):
            return DataCategory.BIOMETRIC

        if any(word in lower_text for word in [
            "genetic",
            "dna",
            "genome"
        ]):
            return DataCategory.GENETIC

        if any(word in lower_text for word in [
            "child",
            "children",
            "minor",
            "pediatric"
        ]):
            return DataCategory.CHILDREN

        if any(word in lower_text for word in [
            "score",
            "scoring",
            "profiling",
            "automated decision"
        ]):
            return DataCategory.PROFILING

        return None

    @classmethod
    def _infer_legal_basis(cls, lower_text):
        if "consent" in lower_text:
            return "consent"

        if any(word in lower_text for word in [
            "contract",
            "application",
            "loan",
            "offer",
            "customer"
        ]):
            return "contract"

        if any(word in lower_text for word in [
            "hospital",
            "patient",
            "medical",
            "sepsis",
            "government",
            "compliance"
        ]):
            return "legal_obligation"

        label = cls._classify(
            lower_text,
            cls.LEGAL_BASIS_LABELS,
            "The GDPR legal basis is {}."
        )

        if label == "legal obligation":
            return "legal_obligation"

        return label

    @staticmethod
    def _infer_data_subject_type(lower_text):
        if any(word in lower_text for word in ["patient", "sepsis", "hospital"]):
            return "patient"

        if any(word in lower_text for word in ["customer", "client", "loan"]):
            return "customer"

        if any(word in lower_text for word in ["student", "education"]):
            return "student"

        if any(word in lower_text for word in ["employee", "hr", "human resources"]):
            return "employee"

        return "data_subject"

    @staticmethod
    def _infer_retention_period(lower_text):
        if any(word in lower_text for word in [
            "hospital",
            "patient",
            "medical",
            "sepsis",
            "government"
        ]):
            return "legal_requirement"

        return "indefinite"

    @staticmethod
    def _has_third_party_recipients(lower_text):
        return any(word in lower_text for word in [
            "third party",
            "external",
            "partner",
            "provider",
            "processor"
        ])

    @staticmethod
    def _infer_international_transfer(lower_text):
        if any(word in lower_text for word in [
            "international",
            "cross-border",
            "third country",
            "outside eu",
            "outside european"
        ]):
            return "third_country"

        return "none"

    @staticmethod
    def _infer_transfer_safeguard(lower_text):
        if any(word in lower_text for word in [
            "scc",
            "standard contractual",
            "adequacy",
            "bcr"
        ]):
            return "safeguard_verified"

        return "none"

from enum import Enum

class DataCategory(Enum):
    # Basado en la tabla de cumplimiento RGPD
    STANDARD = "standard"
    SPECIAL = "special_categories"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    GENETIC = "genetic"
    CHILDREN = "children"
    VULNERABLE = "vulnerable_individuals"
    PROFILING = "automated_decision_profiling"
    INTERNATIONAL_TRANSFER = "international_transfer"
    RESEARCH = "research_statistical"

    @classmethod
    def get_risk_level(cls, category):
        """
        Retorna el nivel de riesgo asociado según la tabla técnica.
        """
        risk_map = {
            cls.STANDARD: "Medium",
            cls.SPECIAL: "High",
            cls.HEALTH: "Very High",
            cls.BIOMETRIC: "Very High",
            cls.GENETIC: "Very High",
            cls.CHILDREN: "High",
            cls.VULNERABLE: "High",
            cls.PROFILING: "High",
            cls.INTERNATIONAL_TRANSFER: "High",
            cls.RESEARCH: "Medium"
        }
        return risk_map.get(category, "Unknown")
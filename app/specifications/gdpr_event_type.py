class GDPREventType:

    _registry = {}

    def __init__(self, name, category, description):

        self.name = name
        self.category = category
        self.description = description

        GDPREventType._registry[name] = self

    def __repr__(self):
        return f"GDPREventType({self.name})"

    @classmethod
    def get_all(cls):
        return list(cls._registry.values())

    @classmethod
    def get_by_name(cls, name):
        return cls._registry.get(name)
    
    
CONSENT_OBTAINED = GDPREventType(
    "consent_obtained",
    "collection",
    "User consent must be obtained"
)

ACCESS_LOG = GDPREventType(
    "access_log",
    "accountability",
    "Access must be logged"
)

MINIMISATION_CHECK = GDPREventType(
    "minimisation_check",
    "processing",
    "Check data minimisation principle"
)

TRANSFER_SAFEGUARD = GDPREventType(
    "transfer_safeguard",
    "transfer",
    "Ensure safeguards for transfer"
)

RETENTION_DECISION = GDPREventType(
    "retention_decision",
    "storage",
    "Define retention policy"
)
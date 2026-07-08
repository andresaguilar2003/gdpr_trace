from enum import Enum


class MutationCategory(Enum):

    STRUCTURAL = "structural"

    TEMPORAL = "temporal"

    CONTEXTUAL = "contextual"

    SEMANTIC = "semantic"
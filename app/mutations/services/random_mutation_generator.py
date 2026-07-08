import random

from app.mutations.registry.mutation_registry import (
    MUTATION_REGISTRY
)


class RandomMutationGenerator:

    @staticmethod
    def generate(count):

        count = min(
            count,
            len(MUTATION_REGISTRY)
        )

        return random.sample(
            list(MUTATION_REGISTRY.keys()),
            count
        )
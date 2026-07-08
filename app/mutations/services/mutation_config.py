from dataclasses import dataclass


@dataclass
class MutationConfig:

    mutation_name: str

    start_trace: int
    end_trace: int

    probability: float = 1.0

    enabled: bool = True
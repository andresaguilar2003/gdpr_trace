from dataclasses import dataclass


@dataclass
class DatasetExample:

    input_text: str

    target_text: str
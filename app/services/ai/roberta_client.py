import torch
from transformers import pipeline


class RobertaClient:

    MODEL = "FacebookAI/roberta-large-mnli"

    _classifier = None

    @classmethod
    def classifier(cls):
        if cls._classifier is None:
            device = 0 if torch.cuda.is_available() else -1
            cls._classifier = pipeline(
                "zero-shot-classification",
                model=cls.MODEL,
                device=device
            )

        return cls._classifier

    @classmethod
    def classify(cls, text, labels, hypothesis_template="This text is about {}."):
        if not labels:
            return None, 0.0

        result = cls.classifier()(
            text,
            candidate_labels=labels,
            hypothesis_template=hypothesis_template,
            multi_label=False
        )

        return result["labels"][0], float(result["scores"][0])

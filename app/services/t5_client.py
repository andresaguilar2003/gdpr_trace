from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


class T5Client:

    def __init__(self):

        self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
        self.model = T5ForConditionalGeneration.from_pretrained("t5-small")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model.to(self.device)

    def ask(self, prompt, max_tokens=20):

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_length=max_tokens
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
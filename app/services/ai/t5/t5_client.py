from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


class T5Client:

    def __init__(self, model_name_or_path="t5-small"):
        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.tokenizer = (
            T5Tokenizer.from_pretrained(
                model_name_or_path
            )
        )

        self.model = (
            T5ForConditionalGeneration
            .from_pretrained(
                model_name_or_path
            )
        )

        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt,
        max_input_length=384,
        max_output_length=64
    ):

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_input_length
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_output_length,
                do_sample=False,
                num_beams=1,
                use_cache=True
            )

        return self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

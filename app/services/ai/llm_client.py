import ollama


class LLMClient:

    MODEL = "phi3:latest"

    @staticmethod
    def ask(prompt: str) -> str:

        response = ollama.chat(
            model=LLMClient.MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "num_predict": 512
            }
        )

        return response["message"]["content"]
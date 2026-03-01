from groq import Groq
import api_keys


class GroqLLM:
    """
    Simple adapter so Groq works with expansion engine.
    Provides: llm.invoke(prompt)
    """

    def __init__(
        self,
        model="llama-3.3-70b-versatile",
        temperature=0.2
    ):
        self.client = Groq()
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str) -> str:

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content #type: ignore
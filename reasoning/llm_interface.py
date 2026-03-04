# reasoning/llm_interface.py

from groq import Groq
import api_keys


def generate_reasoning_text(prompt: str) -> str:
    client = Groq()

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        # max_tokens=1200,
    )

    return response.choices[0].message.content
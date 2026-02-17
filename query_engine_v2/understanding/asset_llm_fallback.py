from groq import Groq
import api_keys


_client = None


def _get_client():
    global _client

    if _client is not None:
        return _client

    try:
        _client = Groq()
    except Exception:
        _client = None

    return _client


def normalize_asset_name(candidate: str | None) -> str | None:
    if not candidate:
        return None

    client = _get_client()
    if client is None:
        return None

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Normalize financial asset names into official company or asset names. "
                        "Return ONLY the normalized name. If unsure return NONE."
                    ),
                },
                {
                    "role": "user",
                    "content": candidate,
                },
            ],
        )

        text = completion.choices[0].message.content.strip() #type: ignore

        if text.upper() == "NONE":
            return None

        return text

    except Exception:
        return None
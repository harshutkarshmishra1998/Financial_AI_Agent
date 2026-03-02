
import re

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"subscribe.*?$", "", text, flags=re.I)
    text = re.sub(r"read more.*?$", "", text, flags=re.I)
    return text.strip()

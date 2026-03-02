
def compress(chunks, max_chars=1200):
    out = []
    for c in chunks:
        out.append(c[:max_chars])
    return out

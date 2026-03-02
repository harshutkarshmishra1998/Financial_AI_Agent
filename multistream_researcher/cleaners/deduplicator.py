from sklearn.metrics.pairwise import cosine_similarity

def deduplicate(embeddings, threshold=0.95):
    keep = []
    for i, emb in enumerate(embeddings):
        if not keep:
            keep.append(i)
            continue
        sims = cosine_similarity([emb], [embeddings[j] for j in keep])[0]
        if max(sims) < threshold:
            keep.append(i)
    return keep

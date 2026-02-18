from collections import defaultdict


class NewsSelector:

    def select(self, articles):

        if not articles:
            return []

        # ---------------------------------
        # Deduplicate by URL
        # ---------------------------------
        unique = {}
        for a in articles:
            if a["url"]:
                unique[a["url"]] = a

        articles = list(unique.values())

        # ---------------------------------
        # simple relevance scoring
        # ---------------------------------
        for a in articles:
            text = (a.get("title") or "") + (a.get("content") or "")
            a["relevance_score"] = min(len(text) / 500, 1)

        # ---------------------------------
        # sort by relevance
        # ---------------------------------
        articles.sort(key=lambda x: x["relevance_score"], reverse=True)

        return articles
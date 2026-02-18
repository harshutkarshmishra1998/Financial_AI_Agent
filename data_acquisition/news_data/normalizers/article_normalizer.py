from datetime import datetime


class ArticleNormalizer:

    @staticmethod
    def normalize_newsapi(article):
        return {
            "timestamp": article.get("publishedAt"),
            "title": article.get("title"),
            "content": article.get("content"),
            "source": article.get("source", {}).get("name"),
            "url": article.get("url")
        }

    @staticmethod
    def normalize_gnews(article):
        return {
            "timestamp": article.get("publishedAt"),
            "title": article.get("title"),
            "content": article.get("description"),
            "source": article.get("source", {}).get("name"),
            "url": article.get("url")
        }

    @staticmethod
    def finalize(article):

        if article["timestamp"]:
            article["timestamp"] = str(
                datetime.fromisoformat(
                    article["timestamp"].replace("Z", "+00:00")
                )
            )

        return article
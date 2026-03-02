from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.document_loaders import WebBaseLoader


search = DuckDuckGoSearchResults()


def search_and_load(query, max_results=5):

    results = search.run(query)

    docs = []

    for r in results[:max_results]:
        url = r.get("link")
        if not url:
            continue

        try:
            loader = WebBaseLoader(url)
            data = loader.load()

            for d in data:
                docs.append({
                    "content": d.page_content,
                    "url": url
                })

        except Exception:
            continue

    return docs
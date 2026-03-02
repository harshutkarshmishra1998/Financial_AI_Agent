from langchain_community.document_loaders import WebBaseLoader


def _get_search_tool():
    try:
        from langchain_community.tools import DuckDuckGoSearchResults

        return DuckDuckGoSearchResults(output_format="list")
    except Exception:
        return None


def search_and_load(query, max_results=5):
    search = _get_search_tool()
    if search is None:
        return []

    results = search.run(query)
    if not isinstance(results, list):
        return []

    docs = []

    for r in results[: max(1, max_results)]:
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

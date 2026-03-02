import requests

def fetch_world_bank(indicator, country="IND"):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json"
    r = requests.get(url)
    return r.json()

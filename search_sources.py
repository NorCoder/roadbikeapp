from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote_plus, urljoin
import re

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


@dataclass
class Listing:
    source: str
    title: str
    url: str
    price: Optional[str]


@dataclass
class Source:
    name: str
    search_url_template: str

    def search_url(self, query: str) -> str:
        return self.search_url_template.format(query=quote_plus(query))


SOURCES = [
    Source("FINN", "https://www.finn.no/bap/forsale/search.html?q={query}"),
    Source("Bikeshop", "https://bikeshop.no/sok?q={query}"),
    Source("XXL", "https://www.xxl.no/search?query={query}"),
    Source("Sykkelkomponenter", "https://www.sykkelkomponenter.no/search?query={query}"),
]


def build_query(model: str, color: str, size: str) -> str:
    return f"{model} {color} størrelse {size}"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_price(text: str) -> Optional[str]:
    m = re.search(r"(?:kr\s*)?\d{1,3}(?:[ .]\d{3})*(?:,-)?", text, flags=re.IGNORECASE)
    if not m:
        return None
    return m.group(0)


def fetch_listings(source: Source, query: str, timeout: int = 10, max_items: int = 20) -> List[Listing]:
    url = source.search_url(query)
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    listings: List[Listing] = []
    seen = set()

    q_words = [w.lower() for w in query.split() if len(w) > 1]

    for anchor in soup.find_all("a", href=True):
        title = _normalize_text(anchor.get_text(" "))
        if len(title) < 12:
            continue

        title_l = title.lower()
        if not any(word in title_l for word in q_words):
            continue

        href = anchor["href"]
        full_url = href if href.startswith("http") else urljoin(url, href)

        key = (title_l, full_url)
        if key in seen:
            continue
        seen.add(key)

        context_text = _normalize_text(anchor.parent.get_text(" ")) if anchor.parent else title
        price = _extract_price(context_text)

        listings.append(
            Listing(
                source=source.name,
                title=title,
                url=full_url,
                price=price,
            )
        )

        if len(listings) >= max_items:
            break

    return listings


def search_all_sources(model: str, color: str, size: str, max_items_per_source: int = 20) -> List[Listing]:
    query = build_query(model=model, color=color, size=size)
    all_hits: List[Listing] = []

    for source in SOURCES:
        all_hits.extend(fetch_listings(source, query, max_items=max_items_per_source))

    return all_hits

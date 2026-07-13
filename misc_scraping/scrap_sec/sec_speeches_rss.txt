from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

RSS_URLS = [
    "https://www.sec.gov/news/speeches-statements.rss",
    "https://www.sec.gov/news/pressreleases.rss",
]

# Be a good citizen: use a descriptive User-Agent with contact info
HEADERS = {
    "User-Agent": "joseph.p.janko@outlook.com",
    "Accept-Encoding": "gzip, deflate",
}


@dataclass
class SpeechItem:
    title: str
    link: str
    published: Optional[str]
    description: Optional[str]
    content: Optional[str]


def fetch_rss(url: str) -> bytes:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.content


def parse_rss(xml_bytes: bytes) -> List[SpeechItem]:
    root = ET.fromstring(xml_bytes)

    # Standard RSS: <rss><channel><item>...</item></channel></rss>
    channel = root.find("channel")
    if channel is None:
        return []

    items: List[SpeechItem] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip() or None
        description = (item.findtext("description") or "").strip() or None

        if not link:
            continue

        items.append(
            SpeechItem(
                title=title,
                link=link,
                published=pub_date,
                description=description,
                content=None,  # will fill after fetching article
            )
        )
    return items


def extract_article_text(html: str) -> str:
    """
    Extract main article body text from a SEC news page.

    This uses multiple selectors to be resilient to minor layout changes.
    If none match, falls back to full page text.
    """
    soup = BeautifulSoup(html, "html.parser")

    candidate_selectors = [
        "div.article-body",              # common article body container
        "div.article-body__content",
        "div.page-content article",
        "main article",
        "div#main-content",
    ]

    for selector in candidate_selectors:
        node = soup.select_one(selector)
        if node:
            text = node.get_text("\n", strip=True)
            if text:
                return text

    # Fallback: entire page text
    return soup.get_text("\n", strip=True)


def enrich_with_content(items: List[SpeechItem], pause: float = 0.5) -> None:
    """
    For each RSS item, fetch the article page and fill in `content`.
    Modifies the list in place.
    """
    for i, item in enumerate(items, start=1):
        try:
            print(f"[{i}/{len(items)}] Fetching article: {item.link}")
            resp = requests.get(item.link, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            item.content = extract_article_text(resp.text)
        except Exception as e:
            print(f"  ! Failed to fetch {item.link}: {e}")
            item.content = None

        time.sleep(pause)  # polite delay between requests


def save_to_text_files(
    items: List[SpeechItem],
    output_dir: str | Path = "sec_speeches_text",
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for i, item in enumerate(items, start=1):
        raw_title = item.title or f"speech_{i}"
        safe = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_"
            for c in raw_title
        ).strip()

        if not safe:
            safe = f"speech_{i}"

        safe = safe[:120]

        filename = f"{i:03d}_{safe}.txt"
        path = output_path / filename

        if path.exists():
            print(f"Skipping existing file {path}")
            continue

        lines = [
            f"Title: {item.title}",
            f"Link: {item.link}",
            f"Published: {item.published or ''}",
            "",
        ]

        if item.content:
            lines.append(item.content)
        else:
            lines.append("[No content extracted]")

        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {path}")


def main():
    items: List[SpeechItem] = []

    for rss_url in RSS_URLS:
        print(f"Fetching RSS feed: {rss_url}")
        xml_bytes = fetch_rss(rss_url)

        print("Parsing RSS feed...")
        feed_items = parse_rss(xml_bytes)
        print(f"Found {len(feed_items)} items in RSS.")
        items.extend(feed_items)

    print("Fetching full article content...")
    enrich_with_content(items, pause=0.5)

    save_to_text_files(items)


if __name__ == "__main__":
    main()
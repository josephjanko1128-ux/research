from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


COMMENT_START_URLS = [
    "https://www.sec.gov/rules-regulations/public-comments/s7-2026-20"
]

# Use a descriptive User-Agent with contact info
HEADERS = {
    "User-Agent": "sec-comments-scraper (joseph.p.janko@outlook.com)",
    "Accept-Encoding": "gzip, deflate",
}


@dataclass
class CommentLink:
    url: str
    filename: str


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_html(url: str, session: requests.Session, timeout: int = 30) -> str:
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def discover_comment_links(
    start_url: str,
    base_dir: str | None = None,
    pause: float = 0.5,
) -> List[CommentLink]:
    """
    Crawl all HTML pages under the given SEC comments directory and
    collect links that look like individual comment letter documents
    (PDF, TXT, HTML, DOC, etc.).

    This does not assume a specific pagination structure; instead, it
    follows all HTML pages within the same directory tree.
    """
    session = _make_session()

    if base_dir is None:
        base_dir = start_url.rsplit("/", 1)[0] + "/"

    to_visit: List[str] = [start_url]
    visited: Set[str] = set()
    comment_urls: Set[str] = set()

    letter_exts = (".pdf", ".txt", ".htm", ".html", ".doc", ".docx")

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        print(f"Visiting index page: {url}")

        try:
            html = fetch_html(url, session=session)
        except Exception as e:
            print(f"  ! Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href:
                continue

            full_url = urljoin(url, href)

            if not full_url.startswith(base_dir):
                continue

            lower = full_url.lower()

            if lower.endswith(letter_exts):
                comment_urls.add(full_url)
                continue

            if lower.endswith((".htm", ".html")) and full_url not in visited:
                to_visit.append(full_url)

        time.sleep(pause)

    links: List[CommentLink] = []
    for url in sorted(comment_urls):
        name = url.rsplit("/", 1)[-1] or "comment"
        links.append(CommentLink(url=url, filename=name))

    print(f"Discovered {len(links)} comment letter URLs.")
    return links


def download_comments(
    links: Iterable[CommentLink],
    output_dir: Path | str = "sec_comments",
    pause: float = 0.5,
) -> None:
    """
    Download all comment documents to the given directory.
    Skips files that already exist.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    session = _make_session()

    for i, link in enumerate(links, start=1):
        dest = output_path / link.filename

        if dest.exists():
            print(f"[{i}] Skipping existing file {dest}")
            continue

        print(f"[{i}] Downloading {link.url} -> {dest}")
        try:
            resp = session.get(link.url, timeout=60)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        except Exception as e:
            print(f"  ! Failed to download {link.url}: {e}")
            continue

        time.sleep(pause)


def _issue_code_from_url(start_url: str) -> str:
    """
    Extract the comment file code (e.g. '10-242', '4-862') from a
    comments URL to use in naming the output directory.
    """
    parsed = urlparse(start_url)
    parts = parsed.path.strip("/").split("/")
    for i, part in enumerate(parts):
        if part == "comments" and i + 1 < len(parts):
            return parts[i + 1].replace("-", "_")
    return "comments"


def main() -> None:
    base_dir = Path("comments")
    base_dir.mkdir(parents=True, exist_ok=True)

    for start_url in COMMENT_START_URLS:
        code = _issue_code_from_url(start_url)
        output_dir = base_dir / code
        print(f"Processing comment set {code} from {start_url}")

        links = discover_comment_links(start_url=start_url)
        download_comments(links, output_dir=output_dir)


if __name__ == "__main__":
    main()


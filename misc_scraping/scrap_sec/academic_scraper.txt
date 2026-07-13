from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://microstructure.exchange/"

# Optional: add SSRN abstract URLs here to download their PDFs as well.
# Example:
# SSRN_ABSTRACT_URLS = [
#     "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1234567",
# ]
SSRN_ABSTRACT_URLS: List[str] = []

# Use a descriptive User-Agent with contact info
HEADERS = {
    "User-Agent": "academic-scraper (joseph.p.janko@outlook.com)",
    "Accept-Encoding": "gzip, deflate",
}


@dataclass
class PaperLink:
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


def discover_paper_links(
    base_url: str = BASE_URL,
) -> List[PaperLink]:
    """
    Discover all 'paper' links on the Microstructure Exchange homepage.

    This looks for <a> tags whose visible text contains 'paper' and
    treats their href targets as papers to download.
    """
    session = _make_session()
    html = fetch_html(base_url, session=session)
    soup = BeautifulSoup(html, "html.parser")

    seen_urls: Set[str] = set()
    papers: List[PaperLink] = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        if "paper" not in text:
            continue

        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)

        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        parsed = urlparse(full_url)
        name = Path(parsed.path).name
        if not name:
            name = "paper.pdf"

        # Only keep links that look like PDFs
        if not name.lower().endswith(".pdf"):
            continue

        papers.append(PaperLink(url=full_url, filename=name))

    print(f"Discovered {len(papers)} paper links.")
    return papers


def _ssrn_pdf_link(html: str, base_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue

        if "download" in text or "pdf" in text:
            full_url = urljoin(base_url, href)
            return full_url

    return None


def collect_ssrn_papers(
    abstract_urls: Iterable[str],
    pause: float = 0.5,
) -> List[PaperLink]:
    session = _make_session()
    papers: List[PaperLink] = []

    for i, abstract_url in enumerate(abstract_urls, start=1):
        print(f"[SSRN {i}] Inspecting abstract page: {abstract_url}")
        try:
            html = fetch_html(abstract_url, session=session)
        except Exception as e:
            print(f"  ! Failed to fetch abstract page {abstract_url}: {e}")
            continue

        pdf_url = _ssrn_pdf_link(html, base_url=abstract_url)
        if not pdf_url:
            print(f"  ! No PDF link found on {abstract_url}")
            continue

        parsed = urlparse(pdf_url)
        name = Path(parsed.path).name or "ssrn_paper.pdf"

        papers.append(PaperLink(url=pdf_url, filename=name))
        time.sleep(pause)

    print(f"Discovered {len(papers)} SSRN PDFs.")
    return papers


def download_papers(
    links: Iterable[PaperLink],
    output_dir: Path | str = "microstructure_papers",
    pause: float = 0.5,
) -> None:
    """
    Download all discovered papers to the given directory.
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


def clean_non_pdf_files(directory: Path | str = "microstructure_papers") -> None:
    """
    Delete any non-PDF files from the given directory.
    """
    path = Path(directory)
    if not path.exists():
        return

    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() != ".pdf":
            print(f"Removing non-PDF file {file}")
            file.unlink()


def main() -> None:
    # Ensure microstructure_papers only contains PDFs
    clean_non_pdf_files("microstructure_papers")

    papers = discover_paper_links(BASE_URL)
    download_papers(papers)

    if SSRN_ABSTRACT_URLS:
        ssrn_papers = collect_ssrn_papers(SSRN_ABSTRACT_URLS)
        download_papers(ssrn_papers, output_dir="ssrn_papers")


if __name__ == "__main__":
    main()


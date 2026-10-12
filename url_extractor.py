"""Extract article text from public URLs with basic SSRF protections.

This is a student/demo implementation, not a complete production sandbox.
For public deployment, also restrict outbound network access at infrastructure level.
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse, urljoin

import requests
import trafilatura

MAX_HTML_BYTES = 3_000_000
TIMEOUT = (5, 15)
USER_AGENT = "NewsSummarizerStudentProject/1.0"


class URLExtractionError(ValueError):
    """Raised when a URL cannot safely be fetched or parsed."""


def _validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise URLExtractionError("Only http and https URLs are accepted.")
    if not parsed.hostname:
        raise URLExtractionError("Please enter a complete URL, including the domain.")
    if parsed.username or parsed.password:
        raise URLExtractionError("URLs containing usernames or passwords are not accepted.")
    if parsed.port and parsed.port not in (80, 443):
        raise URLExtractionError("Only standard HTTP/HTTPS ports are accepted.")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost"} or host.endswith(".localhost") or host.endswith(".local"):
        raise URLExtractionError("Local or private network addresses are not accepted.")

    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            addresses = {ipaddress.ip_address(record[4][0]) for record in records}
        except (socket.gaierror, OSError):
            raise URLExtractionError("The domain could not be resolved.") from None

    if not addresses or any(not address.is_global for address in addresses):
        raise URLExtractionError("This URL does not resolve exclusively to public IP addresses.")
    return url


def _fetch_html(url: str) -> tuple[str, str]:
    current = url
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    for _ in range(4):
        _validate_public_url(current)
        try:
            with requests.get(
                current, headers=headers, timeout=TIMEOUT, stream=True,
                allow_redirects=False,
            ) as response:
                if response.is_redirect or response.is_permanent_redirect:
                    location = response.headers.get("Location")
                    if not location:
                        raise URLExtractionError("The website returned an invalid redirect.")
                    current = urljoin(current, location)
                    continue
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    raise URLExtractionError("The URL did not return an HTML page.")
                chunks, size = [], 0
                for chunk in response.iter_content(chunk_size=65536):
                    if not chunk:
                        continue
                    size += len(chunk)
                    if size > MAX_HTML_BYTES:
                        raise URLExtractionError("The webpage is too large to process (3 MB maximum).")
                    chunks.append(chunk)
                encoding = response.encoding or "utf-8"
                return b"".join(chunks).decode(encoding, errors="replace"), current
        except URLExtractionError:
            raise
        except requests.RequestException as exc:
            raise URLExtractionError(f"Could not download the webpage: {exc.__class__.__name__}.") from None
    raise URLExtractionError("Too many redirects. Please try the article's final URL.")


def extract_article_from_url(url: str) -> dict:
    """Return {'text', 'title', 'url'} for an accessible public article."""
    if not url or len(url) > 2048:
        raise URLExtractionError("Please enter a URL under 2,048 characters.")
    html, final_url = _fetch_html(url.strip())
    text = trafilatura.extract(html, url=final_url, include_comments=False, include_tables=False)
    metadata = trafilatura.extract_metadata(html)
    if not text or len(text.strip()) < 80:
        raise URLExtractionError(
            "No readable article text was found. Try pasting the article text instead."
        )
    return {
        "text": text.strip(),
        "title": (metadata.title or "").strip() if metadata else "",
        "url": final_url,
    }

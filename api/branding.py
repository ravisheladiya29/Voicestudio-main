"""Centralized whitelabel brand configuration for the backend.

Mirrors ui/src/config/brand.ts. Keep the two in sync when rebranding again.
Defaults use the `.example` TLD (reserved for documentation per RFC 2606) as
placeholders until real domains exist.
"""

import os

BRAND_NAME = os.getenv("BRAND_NAME", "Zenvoice")
BRAND_WEBSITE_URL = os.getenv("BRAND_WEBSITE_URL", "https://zenvoice.example")
BRAND_API_URL = os.getenv("BRAND_API_URL", "https://api.zenvoice.example")
BRAND_DOCS_URL = os.getenv("BRAND_DOCS_URL", "https://docs.zenvoice.example")


def brand_docs_url(path: str) -> str:
    """Build a documentation URL under the configured docs host."""
    return f"{BRAND_DOCS_URL.rstrip('/')}/{path.lstrip('/')}"


def normalize_brand_text(text: str | None) -> str | None:
    """Rewrite legacy upstream brand strings for API responses."""
    if not text:
        return text
    return text.replace("Dograh", BRAND_NAME)


DEFAULT_MODEL_SERVICE_KEY_NAME = f"Default {BRAND_NAME} Model Service Key"

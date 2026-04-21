"""Load all configuration from source/<cancer>/ YAML files with _shared/ fallback."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

SOURCE_DIR = Path(__file__).parent.parent / "source"
_current_cancer: str = "breast"


def set_cancer(cancer: str):
    """Switch active cancer type and clear all cached configs."""
    global _current_cancer
    cancer_dir = SOURCE_DIR / cancer
    if not cancer_dir.exists():
        available = [d.name for d in SOURCE_DIR.iterdir()
                     if d.is_dir() and not d.name.startswith("_")]
        raise ValueError(
            f"Unknown cancer type '{cancer}'. "
            f"Available: {', '.join(sorted(available))}"
        )
    _current_cancer = cancer
    # Clear all lru_cache so configs reload from new directory
    for fn in [keywords, drug_groups, conference_keywords,
               search_queries, web_sources, http_headers,
               twitter, journals, crossref_email, disease_label]:
        fn.cache_clear()


def current_cancer() -> str:
    return _current_cancer


def available_cancers() -> list[str]:
    return sorted(d.name for d in SOURCE_DIR.iterdir()
                  if d.is_dir() and not d.name.startswith("_"))


def _load(filename: str) -> Any:
    """Load YAML from cancer-specific dir, fall back to _shared/."""
    cancer_path = SOURCE_DIR / _current_cancer / filename
    if cancer_path.exists():
        return yaml.safe_load(cancer_path.read_text())
    shared_path = SOURCE_DIR / "_shared" / filename
    if shared_path.exists():
        return yaml.safe_load(shared_path.read_text())
    raise FileNotFoundError(
        f"{filename} not found in source/{_current_cancer}/ or source/_shared/"
    )


@lru_cache(maxsize=None)
def disease_label() -> str:
    """Human-readable disease name for display and search queries."""
    data = _load("web_sources.yml")
    return data.get("disease_label", _current_cancer.replace("-", " "))


@lru_cache(maxsize=None)
def keywords() -> list[str]:
    return _load("keywords.yml")["keywords"]


@lru_cache(maxsize=None)
def drug_groups() -> dict[str, list[str]]:
    return _load("drug_groups.yml")["drug_groups"]


@lru_cache(maxsize=None)
def conference_keywords() -> list[str]:
    return _load("drug_groups.yml").get("conference_keywords", [])


@lru_cache(maxsize=None)
def search_queries() -> list[str]:
    return _load("search_queries.yml")["search_queries"]


@lru_cache(maxsize=None)
def web_sources() -> list[dict]:
    return _load("web_sources.yml")["sources"]


@lru_cache(maxsize=None)
def http_headers() -> dict[str, str]:
    return _load("web_sources.yml")["http_headers"]


@lru_cache(maxsize=None)
def twitter() -> dict:
    return _load("twitter.yml")["twitter"]


@lru_cache(maxsize=None)
def journals() -> list[dict]:
    return _load("journals.yml").get("journals", [])


@lru_cache(maxsize=None)
def crossref_email() -> str:
    return _load("journals.yml").get("crossref_email", "")


def seeds_file() -> Path:
    return SOURCE_DIR / _current_cancer / "seeds.txt"

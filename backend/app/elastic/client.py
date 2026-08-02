"""
Thin wrapper around the official elasticsearch-py client.
Only imported/used when ELASTIC_ENABLED=true — keeps the project runnable
with zero external services out of the box.
"""
from app.config.settings import settings

_client = None


def get_es_client():
    global _client
    if _client is not None:
        return _client
    if not settings.ELASTIC_ENABLED:
        raise RuntimeError("Elasticsearch is disabled. Set ELASTIC_ENABLED=true in .env to use it.")
    from elasticsearch import Elasticsearch

    _client = Elasticsearch(
        settings.ELASTIC_URL,
        basic_auth=(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD)
        if settings.ELASTIC_USERNAME else None,
        verify_certs=False,
    )
    return _client


def ping() -> bool:
    try:
        return bool(get_es_client().ping())
    except Exception:
        return False

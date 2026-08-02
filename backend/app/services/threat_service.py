"""
Returns the active data engine (Elasticsearch or local CSV fallback)
based on settings.ELASTIC_ENABLED. Every agent goes through this so the
backend can be pointed at a real Elastic cluster without touching agent
code — set ELASTIC_ENABLED=true and run scripts/ingest_to_elastic.py.
"""
from app.config.settings import settings


def get_data_engine():
    if settings.ELASTIC_ENABLED:
        from app.elastic.queries import elastic_store
        return elastic_store
    from app.data_engine.local_store import local_store
    return local_store

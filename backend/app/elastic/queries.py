"""
Query helpers against Elasticsearch. Mirrors the method surface of
app.data_engine.local_store.LocalStore so agents can use either backend
interchangeably (see app/services/threat_service.py -> get_data_engine()).
"""
from app.elastic.client import get_es_client
from app.config.settings import settings

PREFIX = settings.ELASTIC_INDEX_PREFIX


def _search(index: str, query: dict, size: int = 500):
    es = get_es_client()
    res = es.search(index=index, query=query, size=size)
    return [hit["_source"] for hit in res["hits"]["hits"]]


class ElasticStore:
    def auth_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-auth", q)

    def process_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-process", q)

    def network_events(self, src_ip: str = None):
        q = {"match": {"src_ip": src_ip}} if src_ip else {"match_all": {}}
        return _search(f"{PREFIX}-network", q)

    def dns_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-dns", q)

    def sysmon_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-sysmon", q)

    def registry_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-registry", q)

    def file_events(self, host: str = None):
        q = {"match": {"host": host}} if host else {"match_all": {}}
        return _search(f"{PREFIX}-file", q)

    def threat_intel(self):
        return _search(f"{PREFIX}-threat", {"match_all": {}})

    def mitre_kb(self):
        # MITRE reference data is small & static — served from local CSV even in ES mode.
        from app.data_engine.local_store import local_store
        return local_store.mitre_kb()

    def hosts(self):
        from app.data_engine.local_store import local_store
        return local_store.hosts()

    def users(self):
        from app.data_engine.local_store import local_store
        return local_store.users()

    def lookup_ioc(self, value: str):
        hits = _search(f"{PREFIX}-threat", {"match": {"indicator": value}}, size=1)
        return hits[0] if hits else None


elastic_store = ElasticStore()

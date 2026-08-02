"""
Local data engine — reads the demo CSV dataset with pandas and exposes the
exact same query surface that the Elastic client exposes (see
app/elastic/queries.py). This lets the whole agent pipeline run with zero
external dependencies, and upgrade to a real Elasticsearch cluster later
just by flipping ELASTIC_ENABLED=true in .env (no agent code changes).
"""
import os
import pandas as pd
from functools import lru_cache
from app.config.settings import settings


def _path(name: str) -> str:
    return os.path.join(settings.DATASET_DIR, name)


@lru_cache()
def _load(name: str) -> pd.DataFrame:
    p = _path(name)
    if not os.path.exists(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]
    return df


class LocalStore:
    """Read-only accessor over the CSV dataset, scoped by host / time when asked."""

    def auth_events(self, host: str = None):
        df = _load("authentication_logs.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def process_events(self, host: str = None):
        df = _load("process_events.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def network_events(self, src_ip: str = None):
        df = _load("network_logs.csv")
        if src_ip:
            df = df[df["src_ip"] == src_ip]
        return df.to_dict(orient="records")

    def dns_events(self, host: str = None):
        df = _load("dns_logs.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def sysmon_events(self, host: str = None):
        df = _load("sysmon_events.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def registry_events(self, host: str = None):
        df = _load("registry_events.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def file_events(self, host: str = None):
        df = _load("file_events.csv")
        if host:
            df = df[df["host"] == host]
        return df.to_dict(orient="records")

    def threat_intel(self):
        return _load("threat_intelligence.csv").to_dict(orient="records")

    def mitre_kb(self):
        return _load("mitre_attack.csv").to_dict(orient="records")

    def hosts(self):
        return _load("hosts.csv").to_dict(orient="records")

    def users(self):
        return _load("users.csv").to_dict(orient="records")

    def lookup_ioc(self, value: str):
        intel = self.threat_intel()
        for row in intel:
            if str(row.get("indicator", "")).lower() == value.lower():
                return row
        return None


local_store = LocalStore()

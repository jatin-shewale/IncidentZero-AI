"""
Loads the Operation ShadowFox CSV dataset into a running Elasticsearch
cluster. Only needed if you want to run IncidentZero AI against real
Elasticsearch (ELASTIC_ENABLED=true) instead of the built-in local data
engine.

Usage:
    export ELASTIC_ENABLED=true
    export ELASTIC_URL=http://localhost:9200
    python scripts/ingest_to_elastic.py
"""
import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config.settings import settings
from app.elastic.mappings import INDEXES, PREFIX

FILE_TO_INDEX = {
    "authentication_logs.csv": f"{PREFIX}-auth",
    "process_events.csv": f"{PREFIX}-process",
    "network_logs.csv": f"{PREFIX}-network",
    "dns_logs.csv": f"{PREFIX}-dns",
    "sysmon_events.csv": f"{PREFIX}-sysmon",
    "registry_events.csv": f"{PREFIX}-registry",
    "file_events.csv": f"{PREFIX}-file",
    "threat_intelligence.csv": f"{PREFIX}-threat",
}


def main():
    if not settings.ELASTIC_ENABLED:
        print("ELASTIC_ENABLED is false — set it to true before running this script.")
        sys.exit(1)

    from elasticsearch import Elasticsearch, helpers

    es = Elasticsearch(
        settings.ELASTIC_URL,
        basic_auth=(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD)
        if settings.ELASTIC_USERNAME else None,
        verify_certs=False,
    )
    if not es.ping():
        print(f"Could not reach Elasticsearch at {settings.ELASTIC_URL}")
        sys.exit(1)

    # 1. Create indexes
    for index_name, body in INDEXES.items():
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name, mappings=body["mappings"])
        print(f"Created index: {index_name}")

    # 2. Bulk load each CSV
    for filename, index_name in FILE_TO_INDEX.items():
        path = os.path.join(settings.DATASET_DIR, filename)
        if not os.path.exists(path):
            print(f"Skipping {filename} (not found)")
            continue
        actions = []
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                actions.append({"_index": index_name, "_source": row})
        if actions:
            helpers.bulk(es, actions)
            print(f"Indexed {len(actions)} docs -> {index_name}")

    print("\nDone. Elasticsearch is ready for IncidentZero AI.")


if __name__ == "__main__":
    main()

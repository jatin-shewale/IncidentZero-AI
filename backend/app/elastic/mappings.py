"""
Index definitions for the IncidentZero security data model.
Used by scripts/ingest_to_elastic.py to create indexes before loading CSVs.
"""
from app.config.settings import settings

PREFIX = settings.ELASTIC_INDEX_PREFIX

INDEXES = {
    f"{PREFIX}-auth": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "event_id": {"type": "keyword"},
                "user": {"type": "keyword"},
                "host": {"type": "keyword"},
                "source_ip": {"type": "ip"},
                "login_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "privilege_level": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-process": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "host": {"type": "keyword"},
                "user": {"type": "keyword"},
                "parent_process": {"type": "keyword"},
                "process_name": {"type": "keyword"},
                "command_line": {"type": "text"},
                "hash": {"type": "keyword"},
                "signature": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-network": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "src_ip": {"type": "ip"},
                "destination_ip": {"type": "ip"},
                "destination_port": {"type": "integer"},
                "protocol": {"type": "keyword"},
                "bytes_sent": {"type": "long"},
                "domain": {"type": "keyword"},
                "action": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-dns": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "host": {"type": "keyword"},
                "query": {"type": "keyword"},
                "response_ip": {"type": "ip"},
                "type": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-sysmon": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "event_id": {"type": "integer"},
                "host": {"type": "keyword"},
                "user": {"type": "keyword"},
                "process": {"type": "keyword"},
                "parent": {"type": "keyword"},
                "target": {"type": "text"},
                "details": {"type": "text"},
            }
        }
    },
    f"{PREFIX}-registry": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "host": {"type": "keyword"},
                "user": {"type": "keyword"},
                "key": {"type": "keyword"},
                "value": {"type": "keyword"},
                "action": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-file": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "host": {"type": "keyword"},
                "file_path": {"type": "keyword"},
                "operation": {"type": "keyword"},
                "size": {"type": "long"},
                "hash": {"type": "keyword"},
            }
        }
    },
    f"{PREFIX}-threat": {
        "mappings": {
            "properties": {
                "indicator": {"type": "keyword"},
                "type": {"type": "keyword"},
                "threat": {"type": "keyword"},
                "confidence": {"type": "integer"},
                "source": {"type": "keyword"},
            }
        }
    },
}

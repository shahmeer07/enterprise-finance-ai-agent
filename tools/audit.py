import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("logs/audit.jsonl")


def log_action(action_type, payload):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action_type,
        "payload": payload
    }

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
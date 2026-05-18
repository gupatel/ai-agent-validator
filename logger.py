"""
logger.py — Structured logging for the AI agent validation pipeline.

Writes JSON logs to logs/ directory and maintains a session summary.
"""

import json
import os
import time
from typing import Any


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_run(agent_response: dict, pipeline_summary: dict) -> str:
    """
    Persist a single agent run + validation result to a JSON log file.
    Returns the path of the log file written.
    """
    _ensure_log_dir()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"run_{timestamp}.json"
    path = os.path.join(LOG_DIR, filename)

    entry = {
        "timestamp": agent_response.get("timestamp"),
        "task": agent_response.get("task"),
        "model": agent_response.get("model"),
        "latency_ms": agent_response.get("latency_ms"),
        "agent_status": agent_response.get("status"),
        "validation": pipeline_summary,
    }

    with open(path, "w") as f:
        json.dump(entry, f, indent=2)

    return path


def load_all_logs() -> list[dict]:
    """Load and return all run logs sorted by timestamp (newest first)."""
    _ensure_log_dir()
    logs = []
    for fname in sorted(os.listdir(LOG_DIR), reverse=True):
        if fname.endswith(".json"):
            with open(os.path.join(LOG_DIR, fname)) as f:
                try:
                    logs.append(json.load(f))
                except json.JSONDecodeError:
                    pass
    return logs

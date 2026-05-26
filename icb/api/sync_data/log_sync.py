from main import app
import os
import json

LOG_DIR = "log/sync"

@app.get("/api/v1/sync-logs", tags=['Sync Log'])
def list_sync_logs():
    logs = []
    for filename in sorted(os.listdir(LOG_DIR), reverse=True):
        if filename.endswith(".log"):
            path = os.path.join(LOG_DIR, filename)
            with open(path, "r") as f:
                entries = [json.loads(line) for line in f]
                logs.append({
                    "filename": filename,
                    "transaction_count": len(entries),
                    "total_records_synced": sum(e["record_count"] for e in entries),
                    "success_count": sum(1 for e in entries if e["status"] == "success"),
                    "failure_count": sum(1 for e in entries if e["status"] == "failed")
                })
    return logs

@app.get("/api/v1/sync-logs/{filename}", tags=['Sync Log'])
def get_log_detail(filename: str):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(path):
        return {"error": "Log file not found"}

    with open(path, "r") as f:
        entries = [json.loads(line) for line in f]

    return {
        "filename": filename,
        "stats": entries
    }

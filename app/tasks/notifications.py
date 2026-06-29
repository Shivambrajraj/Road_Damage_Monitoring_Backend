# app/tasks/notifications.py
from app.core.logging import logger

def dispatch_async_incident_broadcast(report_id: int, severity: str):
    """Simulates pushing real-time emergency text notifications to maintenance workers."""
    if severity.lower() == "high":
        logger.info(f"[ASYNC TASK] Urgent alert dispatched to emergency crews for report identifier: #{report_id}")
    else:
        logger.info(f"[ASYNC TASK] Queueing non-critical review notification for report #{report_id}")
import threading
import time
from typing import Callable, Dict, List, Optional
from pathlib import Path

class NewsScheduler:
    def __init__(self, ingest_callback: Callable, post_callback: Optional[Callable] = None):
        self.ingest_callback = ingest_callback
        self.post_callback = post_callback
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.schedules = {
            "ingestion": {"enabled": False, "frequency": "daily", "time": "09:00", "days": ["monday"]},
            "posting": {"enabled": False, "frequency": "daily", "time": "10:00", "days": ["monday"]},
        }

    def load_schedules(self) -> Dict:
        return self.schedules

    def save_schedules(self):
        pass

    def set_ingestion_schedule(self, enabled: bool, frequency: str = "daily", time: str = "09:00", days: Optional[List[str]] = None):
        self.schedules["ingestion"] = {
            "enabled": enabled,
            "frequency": frequency,
            "time": time,
            "days": days or ["monday"],
        }

    def set_posting_schedule(self, enabled: bool, frequency: str = "daily", time: str = "10:00", days: Optional[List[str]] = None):
        self.schedules["posting"] = {
            "enabled": enabled,
            "frequency": frequency,
            "time": time,
            "days": days or ["monday"],
        }

    def _run(self):
        while self.is_running:
            time.sleep(0.1)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run, daemon=True)
        self.scheduler_thread.start()

    def stop(self):
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)

    def run_now(self, job_type: str = "ingestion"):
        if job_type == "ingestion":
            self.ingest_callback()
        elif job_type == "posting" and self.post_callback:
            self.post_callback()

    def get_status(self) -> Dict:
        return {"is_running": self.is_running, "schedules": self.schedules, "next_run": {}}

_scheduler_instance: Optional[NewsScheduler] = None

def get_scheduler() -> NewsScheduler:
    if _scheduler_instance is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    return _scheduler_instance

def init_scheduler(ingest_callback: Callable, post_callback: Optional[Callable] = None) -> NewsScheduler:
    global _scheduler_instance
    _scheduler_instance = NewsScheduler(ingest_callback, post_callback)
    return _scheduler_instance

# Backwards compatibility
Scheduler = NewsScheduler

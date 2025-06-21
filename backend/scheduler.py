import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsScheduler:
    """
    A scheduling system for automated news gathering and posting.
    """
    
    def __init__(self, ingest_callback: Callable, post_callback: Optional[Callable] = None):
        """
        Initialize the scheduler.
        
        Args:
            ingest_callback: Function to call for news ingestion
            post_callback: Function to call for posting curated articles
        """
        self.ingest_callback = ingest_callback
        self.post_callback = post_callback
        self.scheduler_thread = None
        self.is_running = False
        self.schedules_file = Path("schedules.json")
        self.schedules = self.load_schedules()
        
    def load_schedules(self) -> Dict:
        """Load saved schedules from file."""
        if self.schedules_file.exists():
            try:
                with open(self.schedules_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading schedules: {e}")
        return {
            "ingestion": {
                "enabled": False,
                "frequency": "daily",
                "time": "09:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            },
            "posting": {
                "enabled": False,
                "frequency": "daily",
                "time": "10:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
        }
    
    def save_schedules(self):
        """Save schedules to file."""
        try:
            with open(self.schedules_file, 'w') as f:
                json.dump(self.schedules, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
    
    def set_ingestion_schedule(self, enabled: bool, frequency: str = "daily", 
                              time: str = "09:00", days: Optional[List[str]] = None):
        """
        Set the ingestion schedule.
        
        Args:
            enabled: Whether ingestion is enabled
            frequency: 'hourly', 'daily', 'weekly'
            time: Time in HH:MM format
            days: List of days for weekly schedule
        """
        self.schedules["ingestion"] = {
            "enabled": enabled,
            "frequency": frequency,
            "time": time,
            "days": days or ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
        self.save_schedules()
        self.setup_schedules()
        logger.info(f"Ingestion schedule updated: {self.schedules['ingestion']}")
    
    def set_posting_schedule(self, enabled: bool, frequency: str = "daily", 
                           time: str = "10:00", days: Optional[List[str]] = None):
        """
        Set the posting schedule.
        
        Args:
            enabled: Whether posting is enabled
            frequency: 'hourly', 'daily', 'weekly'
            time: Time in HH:MM format
            days: List of days for weekly schedule
        """
        self.schedules["posting"] = {
            "enabled": enabled,
            "frequency": frequency,
            "time": time,
            "days": days or ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
        self.save_schedules()
        self.setup_schedules()
        logger.info(f"Posting schedule updated: {self.schedules['posting']}")
    
    def setup_schedules(self):
        """Setup the scheduled jobs."""
        schedule.clear()
        
        # Setup ingestion schedule
        if self.schedules["ingestion"]["enabled"]:
            self._setup_ingestion_job()
        
        # Setup posting schedule
        if self.schedules["posting"]["enabled"]:
            self._setup_posting_job()
    
    def _setup_ingestion_job(self):
        """Setup the ingestion job based on frequency."""
        config = self.schedules["ingestion"]
        frequency = config["frequency"]
        time_str = config["time"]
        
        if frequency == "hourly":
            schedule.every().hour.at(time_str).do(self._run_ingestion)
        elif frequency == "daily":
            schedule.every().day.at(time_str).do(self._run_ingestion)
        elif frequency == "weekly":
            for day in config["days"]:
                getattr(schedule.every(), day).at(time_str).do(self._run_ingestion)
        
        logger.info(f"Ingestion job scheduled: {frequency} at {time_str}")
    
    def _setup_posting_job(self):
        """Setup the posting job based on frequency."""
        config = self.schedules["posting"]
        frequency = config["frequency"]
        time_str = config["time"]
        
        if frequency == "hourly":
            schedule.every().hour.at(time_str).do(self._run_posting)
        elif frequency == "daily":
            schedule.every().day.at(time_str).do(self._run_posting)
        elif frequency == "weekly":
            for day in config["days"]:
                getattr(schedule.every(), day).at(time_str).do(self._run_posting)
        
        logger.info(f"Posting job scheduled: {frequency} at {time_str}")
    
    def _run_ingestion(self):
        """Run the ingestion job."""
        try:
            logger.info("Running scheduled ingestion...")
            result = self.ingest_callback()
            logger.info(f"Ingestion completed: {result}")
        except Exception as e:
            logger.error(f"Error during scheduled ingestion: {e}")
    
    def _run_posting(self):
        """Run the posting job."""
        if not self.post_callback:
            logger.warning("No posting callback configured")
            return
        
        try:
            logger.info("Running scheduled posting...")
            result = self.post_callback()
            logger.info(f"Posting completed: {result}")
        except Exception as e:
            logger.error(f"Error during scheduled posting: {e}")
    
    def start(self):
        """Start the scheduler in a separate thread."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.setup_schedules()
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get the current status of the scheduler."""
        return {
            "is_running": self.is_running,
            "schedules": self.schedules,
            "next_run": self._get_next_run_times()
        }
    
    def _get_next_run_times(self) -> Dict:
        """Get the next run times for scheduled jobs."""
        next_runs = {}
        
        if schedule.jobs:
            for job in schedule.jobs:
                if hasattr(job, 'next_run'):
                    next_runs[job.job_func.__name__] = job.next_run.isoformat()
        
        return next_runs
    
    def run_now(self, job_type: str = "ingestion"):
        """
        Run a job immediately.
        
        Args:
            job_type: 'ingestion' or 'posting'
        """
        try:
            if job_type == "ingestion":
                logger.info("Running ingestion now...")
                result = self.ingest_callback()
                logger.info(f"Manual ingestion completed: {result}")
            elif job_type == "posting" and self.post_callback:
                logger.info("Running posting now...")
                result = self.post_callback()
                logger.info(f"Manual posting completed: {result}")
            else:
                logger.error(f"Invalid job type: {job_type}")
        except Exception as e:
            logger.error(f"Error running {job_type}: {e}")


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> NewsScheduler:
    """Get the global scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    return _scheduler_instance


def init_scheduler(ingest_callback: Callable, post_callback: Optional[Callable] = None) -> NewsScheduler:
    """
    Initialize the global scheduler instance.
    
    Args:
        ingest_callback: Function to call for news ingestion
        post_callback: Function to call for posting curated articles
    
    Returns:
        The scheduler instance
    """
    global _scheduler_instance
    _scheduler_instance = NewsScheduler(ingest_callback, post_callback)
    return _scheduler_instance


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()


# Utility functions for common scheduling patterns
def setup_daily_ingestion(time: str = "09:00"):
    """Setup daily ingestion at the specified time."""
    scheduler = get_scheduler()
    scheduler.set_ingestion_schedule(True, "daily", time)


def setup_weekly_ingestion(time: str = "09:00", days: Optional[List[str]] = None):
    """Setup weekly ingestion on specified days."""
    if days is None:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    scheduler = get_scheduler()
    scheduler.set_ingestion_schedule(True, "weekly", time, days)


def setup_hourly_ingestion():
    """Setup hourly ingestion."""
    scheduler = get_scheduler()
    scheduler.set_ingestion_schedule(True, "hourly", "00:00")


def disable_ingestion():
    """Disable ingestion scheduling."""
    scheduler = get_scheduler()
    scheduler.set_ingestion_schedule(False)


def setup_daily_posting(time: str = "10:00"):
    """Setup daily posting at the specified time."""
    scheduler = get_scheduler()
    scheduler.set_posting_schedule(True, "daily", time)


def disable_posting():
    """Disable posting scheduling."""
    scheduler = get_scheduler()
    scheduler.set_posting_schedule(False) 

# Scheduler alias for compatibility
Scheduler = NewsScheduler 

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


def setup_logging(enable_file: bool = True, log_level: str = "INFO", **kwargs) -> None:
    logging.basicConfig(level=getattr(logging, log_level))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, response_time: float, user_agent: str = "", ip_address: str = "") -> None:
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time": response_time,
        "user_agent": user_agent,
        "ip_address": ip_address,
    }))


def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, success: bool, response_time: float, error_message: str = "") -> None:
    logger.info(json.dumps({
        "api_name": api_name,
        "endpoint": endpoint,
        "success": success,
        "response_time": response_time,
        "error_message": error_message,
    }))


def log_article_processing(logger: logging.Logger, action: str, article_id: str, source: str, success: bool, error_message: str = "") -> None:
    logger.info(json.dumps({
        "action": action,
        "article_id": article_id,
        "source": source,
        "success": success,
        "error_message": error_message,
    }))


def log_scheduler_event(logger: logging.Logger, event_type: str, job_name: str, success: bool, result: Dict[str, Any] | None = None, error_message: str = "") -> None:
    logger.info(json.dumps({
        "event_type": event_type,
        "job_name": job_name,
        "success": success,
        "result": result,
        "error_message": error_message,
    }))


def get_log_files() -> Dict[str, str]:
    return {f.name: str(f) for f in logs_dir.glob("*.log*")}


def clear_logs() -> None:
    for f in logs_dir.glob("*.log*"):
        f.unlink(missing_ok=True)


def get_log_stats() -> Dict[str, Any]:
    files = list(logs_dir.glob("*.log*"))
    return {
        "total_files": len(files),
        "total_size": sum(f.stat().st_size for f in files),
        "files": {f.name: {"size": f.stat().st_size} for f in files},
    }

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class RequestFormatter(logging.Formatter):
    """Formatter for HTTP request logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add request-specific fields
        extra_fields = getattr(record, 'extra_fields', {})
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "method": extra_fields.get('method', ''),
            "path": extra_fields.get('path', ''),
            "status_code": extra_fields.get('status_code', ''),
            "response_time": extra_fields.get('response_time', ''),
            "user_agent": extra_fields.get('user_agent', ''),
            "ip_address": extra_fields.get('ip_address', '')
        }
        
        return json.dumps(log_entry)


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "app.log",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Name of the log file
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Whether to log to console
        enable_file: Whether to log to file
    """
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_formatter = JSONFormatter()
    
    # Create handlers
    handlers = []
    
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(console_handler)
    
    if enable_file:
        # Main application log
        app_log_file = logs_dir / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(file_handler)
        
        # Error log (only errors and critical)
        error_log_file = logs_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        handlers.append(error_handler)
        
        # Request log
        request_log_file = logs_dir / "requests.log"
        request_handler = logging.handlers.RotatingFileHandler(
            request_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        request_handler.setFormatter(RequestFormatter())
        request_handler.setLevel(logging.INFO)
        handlers.append(request_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    response_time: float,
    user_agent: str = "",
    ip_address: str = ""
) -> None:
    """
    Log HTTP request information.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        response_time: Response time in seconds
        user_agent: User agent string
        ip_address: Client IP address
    """
    extra_fields = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'response_time': f"{response_time:.3f}s",
        'user_agent': user_agent,
        'ip_address': ip_address
    }
    
    # Create a new log record with extra fields
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "",
        0,
        f"{method} {path} - {status_code} ({response_time:.3f}s)",
        (),
        None,
        func="log_request"
    )
    record.extra_fields = extra_fields
    
    logger.handle(record)


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    endpoint: str,
    success: bool,
    response_time: float,
    error_message: str = ""
) -> None:
    """
    Log API call information.
    
    Args:
        logger: Logger instance
        api_name: Name of the API (e.g., "NewsData", "OpenAI")
        endpoint: API endpoint
        success: Whether the call was successful
        response_time: Response time in seconds
        error_message: Error message if call failed
    """
    level = logging.INFO if success else logging.ERROR
    message = f"API call to {api_name} - {endpoint}"
    
    if not success:
        message += f" - Error: {error_message}"
    
    extra_fields = {
        'api_name': api_name,
        'endpoint': endpoint,
        'success': success,
        'response_time': f"{response_time:.3f}s"
    }
    
    if error_message:
        extra_fields['error_message'] = error_message
    
    record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        (),
        None,
        func="log_api_call"
    )
    record.extra_fields = extra_fields
    
    logger.handle(record)


def log_article_processing(
    logger: logging.Logger,
    action: str,
    article_id: str,
    source: str,
    success: bool,
    error_message: str = ""
) -> None:
    """
    Log article processing information.
    
    Args:
        logger: Logger instance
        action: Action performed (ingest, select, edit, post)
        article_id: Article ID
        source: Article source
        success: Whether the action was successful
        error_message: Error message if action failed
    """
    level = logging.INFO if success else logging.ERROR
    message = f"Article {action}: {article_id} from {source}"
    
    if not success:
        message += f" - Error: {error_message}"
    
    extra_fields = {
        'action': action,
        'article_id': article_id,
        'source': source,
        'success': success
    }
    
    if error_message:
        extra_fields['error_message'] = error_message
    
    record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        (),
        None,
        func="log_article_processing"
    )
    record.extra_fields = extra_fields
    
    logger.handle(record)


def log_scheduler_event(
    logger: logging.Logger,
    event_type: str,
    job_name: str,
    success: bool,
    result: Optional[Dict[str, Any]] = None,
    error_message: str = ""
) -> None:
    """
    Log scheduler event information.
    
    Args:
        logger: Logger instance
        event_type: Type of event (start, stop, run, error)
        job_name: Name of the job
        success: Whether the event was successful
        result: Result of the job execution
        error_message: Error message if event failed
    """
    level = logging.INFO if success else logging.ERROR
    message = f"Scheduler {event_type}: {job_name}"
    
    if not success:
        message += f" - Error: {error_message}"
    
    extra_fields = {
        'event_type': event_type,
        'job_name': job_name,
        'success': success
    }
    
    if result:
        extra_fields['result'] = result
    
    if error_message:
        extra_fields['error_message'] = error_message
    
    record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        (),
        None,
        func="log_scheduler_event"
    )
    record.extra_fields = extra_fields
    
    logger.handle(record)


def get_log_files() -> Dict[str, str]:
    """
    Get list of available log files.
    
    Returns:
        Dictionary mapping log file names to their paths
    """
    log_files = {}
    
    for log_file in logs_dir.glob("*.log*"):
        log_files[log_file.name] = str(log_file)
    
    return log_files


def clear_logs() -> None:
    """Clear all log files."""
    for log_file in logs_dir.glob("*.log*"):
        try:
            log_file.unlink()
        except Exception as e:
            print(f"Error deleting log file {log_file}: {e}")


def get_log_stats() -> Dict[str, Any]:
    """
    Get statistics about log files.
    
    Returns:
        Dictionary with log file statistics
    """
    stats = {
        "total_files": 0,
        "total_size": 0,
        "files": {}
    }
    
    for log_file in logs_dir.glob("*.log*"):
        try:
            file_size = log_file.stat().st_size
            stats["total_files"] += 1
            stats["total_size"] += file_size
            stats["files"][log_file.name] = {
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            }
        except Exception as e:
            print(f"Error getting stats for {log_file}: {e}")
    
    return stats


# Initialize logging when module is imported
setup_logging()

# Create logger instances for different components
api_logger = get_logger("api")
agent_logger = get_logger("agents")
scheduler_logger = get_logger("scheduler")
database_logger = get_logger("database") 

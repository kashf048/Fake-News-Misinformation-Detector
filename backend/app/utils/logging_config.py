"""
Structured Logging Configuration
Centralized logging setup with structured output
"""

import logging
import json
import os
from datetime import datetime
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging"""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logging():
    """Setup structured logging"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "json")  # json or text

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # File handler
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setLevel(log_level)

    if log_format == "json":
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(logger)s %(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


class StructuredLogger:
    """Structured logging wrapper"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, method: str, path: str, status_code: int, duration: float):
        """Log HTTP request"""
        self.logger.info(
            "HTTP Request",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration * 1000,
            }
        )

    def log_error(self, error_type: str, message: str, **kwargs):
        """Log error with context"""
        self.logger.error(
            f"{error_type}: {message}",
            extra=kwargs
        )

    def log_database_operation(self, operation: str, collection: str, duration: float):
        """Log database operation"""
        self.logger.info(
            "Database Operation",
            extra={
                "operation": operation,
                "collection": collection,
                "duration_ms": duration * 1000,
            }
        )

    def log_model_inference(self, model_name: str, duration: float):
        """Log model inference"""
        self.logger.info(
            "Model Inference",
            extra={
                "model": model_name,
                "duration_ms": duration * 1000,
            }
        )

    def log_user_action(self, user_id: str, action: str, **kwargs):
        """Log user action"""
        self.logger.info(
            f"User Action: {action}",
            extra={
                "user_id": user_id,
                **kwargs
            }
        )

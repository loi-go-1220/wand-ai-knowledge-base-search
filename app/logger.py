"""
Structured logging configuration
Provides consistent logging across the application
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup application logging with consistent format"""
    
    # Create logger
    logger = logging.getLogger("knowledge_base")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics in structured format"""
    logger = logging.getLogger("knowledge_base.performance")
    
    perf_data = {
        "operation": operation,
        "duration_seconds": round(duration, 4),
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    if duration > 5.0:  # Slow operation
        logger.warning(f"Slow operation detected: {operation} took {duration:.2f}s", extra=perf_data)
    elif duration > 2.0:  # Moderate
        logger.info(f"Operation completed: {operation} took {duration:.2f}s", extra=perf_data)
    else:  # Fast
        logger.debug(f"Operation completed: {operation} took {duration:.2f}s", extra=perf_data)

def log_error(operation: str, error: Exception, **kwargs):
    """Log errors in structured format"""
    logger = logging.getLogger("knowledge_base.errors")
    
    error_data = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    logger.error(f"Error in {operation}: {error}", extra=error_data)

# Global logger instance
logger = setup_logging()

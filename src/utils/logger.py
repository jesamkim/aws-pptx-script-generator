"""Logging Configuration Module.

This module provides centralized logging configuration with structured output
and performance monitoring capabilities.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from functools import wraps


def setup_logging(log_file: Optional[str] = None, level: str = "INFO"):
    """Configure logging with custom format and outputs.
    
    Args:
        log_file: Optional path to log file
        level: Minimum log level
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                   "{name}:{function}:{line} | {message}",
            level=level,
            rotation="1 day",
            retention="7 days",
            compression="zip"
        )


def log_execution_time(func):
    """Decorator to log function execution time.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with execution time logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    return wrapper


class PerformanceMonitor:
    """Monitors and logs performance metrics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def start_operation(self, operation_name: str):
        """Start timing an operation.
        
        Args:
            operation_name: Name of operation to monitor
        """
        self.metrics[operation_name] = {
            'start_time': time.time(),
            'status': 'running'
        }
    
    def end_operation(self, operation_name: str, success: bool = True):
        """End timing an operation and log metrics.
        
        Args:
            operation_name: Name of operation
            success: Whether operation completed successfully
        """
        if operation_name in self.metrics:
            end_time = time.time()
            duration = end_time - self.metrics[operation_name]['start_time']
            
            self.metrics[operation_name].update({
                'end_time': end_time,
                'duration': duration,
                'status': 'success' if success else 'failed'
            })
            
            logger.info(
                f"Operation {operation_name} {self.metrics[operation_name]['status']} "
                f"in {duration:.2f} seconds"
            )
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all collected performance metrics.
        
        Returns:
            Dictionary of operation metrics
        """
        return self.metrics
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()


# Initialize global performance monitor
performance_monitor = PerformanceMonitor()

# Configure default logging
setup_logging()

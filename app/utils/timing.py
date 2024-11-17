# app/utils/timing.py
import time
import logging
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

def log_timing(step_name):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {step_name}...")
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {step_name} in {duration:.2f} seconds")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {step_name} after {duration:.2f} seconds: {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {step_name}...")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {step_name} in {duration:.2f} seconds")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {step_name} after {duration:.2f} seconds: {str(e)}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
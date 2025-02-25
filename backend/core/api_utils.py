import logging
import time
from functools import wraps
from typing import Callable, Any, Dict, Optional
from requests.exceptions import RequestException
from jira.exceptions import JIRAError
from openai import OpenAIError, RateLimitError

# Configure logging
logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0,
                      max_delay: float = 10.0, backoff_factor: float = 2.0) -> Callable:
    """Decorator for retrying API calls with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (RequestException, JIRAError, OpenAIError) as e:
                    last_exception = e
                    if isinstance(e, RateLimitError) or \
                       (isinstance(e, JIRAError) and e.status_code == 429):
                        # Handle rate limits specifically
                        retry_after = get_retry_after(e)
                        if retry_after:
                            time.sleep(retry_after)
                            continue

                    # Log the error
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                    )

                    # If this was our last attempt, don't sleep
                    if attempt == max_retries - 1:
                        break

                    # Exponential backoff
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            # If we've exhausted all retries, raise the last exception
            logger.error(f"All {max_retries} retry attempts failed")
            raise last_exception

        return wrapper
    return decorator

def get_retry_after(exception: Exception) -> Optional[float]:
    """Extract retry-after value from various API exceptions."""
    if isinstance(exception, RateLimitError):
        # OpenAI rate limit handling
        return float(getattr(exception, 'retry_after', 30))
    elif isinstance(exception, JIRAError) and exception.status_code == 429:
        # Jira rate limit handling
        response = getattr(exception, 'response', None)
        if response and 'Retry-After' in response.headers:
            return float(response.headers['Retry-After'])
    return None

def format_error_message(error: Exception) -> Dict[str, str]:
    """Format error messages for API responses."""
    if isinstance(error, JIRAError):
        if error.status_code == 404:
            return {
                'error': 'The requested Jira resource was not found.',
                'details': str(error)
            }
        elif error.status_code == 401:
            return {
                'error': 'Authentication failed. Please check your Jira credentials.',
                'details': str(error)
            }
        elif error.status_code == 403:
            return {
                'error': 'You don\'t have permission to perform this action in Jira.',
                'details': str(error)
            }
        elif error.status_code == 429:
            return {
                'error': 'Too many requests to Jira. Please try again later.',
                'details': str(error)
            }
    elif isinstance(error, OpenAIError):
        if isinstance(error, RateLimitError):
            return {
                'error': 'OpenAI rate limit reached. Please try again later.',
                'details': str(error)
            }
        return {
            'error': 'An error occurred while processing your request with OpenAI.',
            'details': str(error)
        }
    
    # Generic error handling
    return {
        'error': 'An unexpected error occurred. Please try again later.',
        'details': str(error)
    }
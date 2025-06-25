import requests
from typing import Dict, Any, Optional
import logging

class ApiClient:
    """Base class for API clients with common functionality"""

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client

        Args:
            api_url: Base URL for the API
            api_key: Optional API key for authentication
        """
        self.logger = logging.getLogger(__name__)
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key} if self.api_key else {}

    def _make_request(self, method: str = "GET", endpoint: str = "", params: Optional[Dict] = None,
                      headers: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to call (appended to base URL)
            params: URL parameters to include
            headers: Additional headers to include
            data: Request body for POST requests

        Returns:
            Dictionary with API response

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        request_headers = self.headers.copy()

        if headers:
            request_headers.update(headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=request_headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making {method} request to {url}: {str(e)}")
            raise

"""
API clients for geocoding and weather data services
"""
from typing import Dict, Any
from src.data_pipeline.ingestion.clients.base import ApiClient


class GeocodingApiClient(ApiClient):
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize the Geocoding API client

        Args:
            api_key: API key for authentication
            api_url: Base URL for the geocoding API
        """
        super().__init__(api_url=api_url, api_key=api_key)

    def geocode_city(self, city_name: str, country: str = None) -> Dict[str, Any]:
        """
        Get geocoding data for a city

        Args:
            city_name: Name of the city to geocode
            country: Optional country code (e.g., 'NL')

        Returns:
            Dictionary with geocoding details
        """
        params = {"city": city_name}
        if country:
            params["country"] = country

        return self._make_request(params=params)

    def get_geocode(self, city_name: str, country: str = None) -> Dict[str, Any]:
        """Alias for geocode_city for compatibility with existing code"""
        return self.geocode_city(city_name, country)


class WeatherApiClient(ApiClient):
    def __init__(self, api_url: str):
        """
        Initialize the Weather API client

        Args:
            api_url: Base URL for the weather API
        """
        super().__init__(api_url=api_url)

    def get_weather_forecast(
            self,
            latitude: float,
            longitude: float,
            forecast_days: int = 7,
            hourly_params: str = "temperature_2m,precipitation,windspeed_10m"
    ) -> Dict[str, Any]:
        """
        Fetch weather forecast from Weather API.

        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            forecast_days: Number of days to forecast (default: 7)
            hourly_params: Comma-separated weather parameters to get hourly data for

        Returns:
            Dictionary containing the weather forecast data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": hourly_params,
            "forecast_days": forecast_days
        }

        return self._make_request(params=params)

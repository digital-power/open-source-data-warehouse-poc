"""
Utility functions for fetching and processing weather forecast data.
"""
from typing import Any
import logging

from src.data_pipeline.ingestion.models.location import Location

# Set up logging
logger = logging.getLogger(__name__)

def fetch_weather_forecasts(geocoded_cities: dict[str, Location], weather_api_client=None) -> list[dict[str, Any]]:
    """
    Fetch raw weather forecast data from weather API for geocoded cities.

    The weather API returns data in this format:
    {
      "current": {
        "time": "2022-01-01T15:00",
        "temperature_2m": 2.4,
        "wind_speed_10m": 11.9,
      },
      "hourly": {
        "time": ["2022-07-01T00:00","2022-07-01T01:00", ...],
        "wind_speed_10m": [3.16,3.02,3.3,3.14,3.2,2.95, ...],
        "temperature_2m": [13.7,13.3,12.8,12.3,11.8, ...],
        "relative_humidity_2m": [82,83,86,85,88,88,84,76, ...],
      }
    }

    Args:
        geocoded_cities: Dictionary mapping city names to Location objects with coordinates
        weather_api_client: API client for weather service

    Returns:
        List of weather forecast data dictionaries
    """
    if weather_api_client is None:
        raise ValueError("Weather API client is required")

    weather_forecasts = []

    for city_key, location in geocoded_cities.items():
        try:
            # Use location coordinates directly from the Location object
            if not location.has_coordinates:
                logger.warning(f"Skipping {city_key} - missing coordinates")
                continue

            logger.info(f"Fetching weather for {city_key} at coordinates: {location.latitude}, {location.longitude}")
            weather_data = weather_api_client.get_weather_forecast(
                latitude=location.latitude,
                longitude=location.longitude
            )

            # Check if weather_data is valid and has the expected structure
            if weather_data and isinstance(weather_data, dict):
                # Check if it has at least one of the expected sections
                has_valid_data = False
                for section in ["current", "hourly", "daily"]:
                    if section in weather_data and isinstance(weather_data[section], dict):
                        has_valid_data = True
                        break

                if has_valid_data:
                    # Add city name to the weather data for reference
                    weather_data["city_name"] = city_key

                    # Store a reference to the original location object (with coordinates)
                    weather_data["location_metadata"] = {
                        "city": location.city_name,
                        "country": location.country,
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    }

                    weather_forecasts.append(weather_data)
                    logger.info(f"Successfully fetched weather data for {city_key}")
                else:
                    logger.warning(f"Weather data for {city_key} missing expected sections")
            else:
                logger.warning(f"Invalid weather data returned for {city_key}: {type(weather_data)}")

        except Exception as e:
            logger.error(f"Error fetching weather data for {city_key}: {str(e)}", exc_info=True)

    logger.info(f"Successfully fetched weather data for {len(weather_forecasts)} cities")

    # Log sample of data structure (without the actual values) for debugging
    if weather_forecasts:
        sample = weather_forecasts[0]
        structure = {k: type(v).__name__ for k, v in sample.items()}
        sample_city = sample.get("city_name", "Unknown")
        logger.info(f"Sample weather data structure for {sample_city}: {structure}")

        # Log available data points in hourly data
        if "hourly" in sample and isinstance(sample["hourly"], dict):
            hourly_keys = list(sample["hourly"].keys())
            logger.info(f"Available hourly data points: {hourly_keys}")

    return weather_forecasts

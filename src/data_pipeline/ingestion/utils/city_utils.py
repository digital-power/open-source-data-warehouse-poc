"""
Utility functions for working with city data.
"""
from pathlib import Path
import logging

from src.data_pipeline.ingestion.models.location import Location
from src.data_pipeline.ingestion.clients.weather import GeocodingApiClient

# Set up logging
logger = logging.getLogger(__name__)

def get_dutch_cities() -> list[Location]:
    """Loads the list of Dutch cities from file."""
    current_file = Path(__file__)
    cities_file_path = current_file.parents[1] / "data" / "dutch_cities.txt"

    logger.info(f"Attempting to load cities from: {cities_file_path}")

    cities = []

    try:
        with open(cities_file_path, "r") as f:
            idx = 0
            for line in f:
                city_name = line.strip()
                if city_name:
                    # Create Location object and add to the list
                    location_obj = Location(city_name=city_name, country="NL")
                    cities.append(location_obj)

                    idx += 1

            logger.info(f"Added {idx} cities to list")

    except FileNotFoundError:
        logger.error(f"{cities_file_path} not found.")
        raise FileNotFoundError(f"Failed to load {cities_file_path}")

    return cities


def geocode_cities(dutch_cities: list[Location], geocoding_api_client: GeocodingApiClient) -> dict[str, Location]:
    """
    Get latitude and longitude for all cities using a geocoding API and return as a dictionary.

    The API returns data in this format:
    [
      {
        "name": "London",
        "latitude": 51.5085,
        "longitude": -0.1257,
        "country": "GB"
      }
    ]

    Args:
        dutch_cities: List of Location objects representing Dutch cities
        geocoding_api_client: API client for geocoding service

    Returns:
        Dictionary mapping city names to Location objects with coordinates
    """
    if geocoding_api_client is None:
        raise ValueError("Geocoding API client is required")

    geocoded_cities = {}

    for city in dutch_cities:
        try:
            geocode_data = geocoding_api_client.get_geocode(city.city_name, city.country)
            logger.debug(f"Received geocode data for {city.city_name}: {geocode_data}")

            # Handle list response which contains location objects
            if isinstance(geocode_data, list) and len(geocode_data) > 0:
                # Take the first result
                location_data = geocode_data[0]

                if isinstance(location_data, dict):
                    # Extract direct latitude/longitude fields
                    if "latitude" in location_data and "longitude" in location_data:
                        city.latitude = float(location_data["latitude"])
                        city.longitude = float(location_data["longitude"])
                        geocoded_cities[city.city_name] = city
                        logger.info(f"Successfully geocoded {city.city_name}: ({city.latitude}, {city.longitude})")
                    else:
                        logger.warning(f"Missing coordinates in geocode data for {city.city_name}")
                else:
                    logger.warning(f"Unexpected format in geocode response for {city.city_name}")

            # Handle direct dictionary response (just in case)
            elif isinstance(geocode_data, dict):
                if "latitude" in geocode_data and "longitude" in geocode_data:
                    city.latitude = float(geocode_data["latitude"])
                    city.longitude = float(geocode_data["longitude"])
                    geocoded_cities[city.city_name] = city
                    logger.info(f"Successfully geocoded {city.city_name}: ({city.latitude}, {city.longitude})")
                else:
                    logger.warning(f"Missing coordinates in geocode data for {city.city_name}")
            else:
                logger.warning(f"No valid geocoding data returned for {city.city_name}")

        except Exception as e:
            logger.error(f"Error geocoding {city.city_name}: {str(e)}", exc_info=True)
            # Implement retry logic here if needed

    # Log summary
    logger.info(f"Successfully geocoded {len(geocoded_cities)} cities out of {len(dutch_cities)} requested")
    return geocoded_cities

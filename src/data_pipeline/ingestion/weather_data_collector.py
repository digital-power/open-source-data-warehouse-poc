"""
Weather Data Collector - Entry point
"""
import logging
from typing import Any
from datetime import datetime

from src.data_pipeline.ingestion.clients.weather import GeocodingApiClient, WeatherApiClient
from src.data_pipeline.ingestion.clients.storage import ScalewayJSONStorage
from src.data_pipeline.ingestion.models.scaleway_storage import ScalewayStorageConfig
from src.data_pipeline.ingestion.models.location import Location
from src.data_pipeline.ingestion.configs.constants import *
from src.data_pipeline.ingestion.utils.city_utils import get_dutch_cities, geocode_cities
from src.data_pipeline.ingestion.utils.weather_utils import fetch_weather_forecasts


class WeatherDataCollector:
    """Collects weather data for specified locations"""

    def __init__(self, use_object_store: bool = True):
        self.logger = logging.getLogger(__name__)
        # Initialize API clients
        self.geocoding_client = GeocodingApiClient(
            api_key=GEOCODING_API_KEY,
            api_url=GEOCODING_API_URL
        )
        self.weather_client = WeatherApiClient(api_url=WEATHER_API_URL)

        # Initialize Scaleway Object Store client
        self.use_object_store = use_object_store
        if self.use_object_store:
            try:
                scaleway_config = ScalewayStorageConfig(
                    access_key=SCALEWAY_ACCESS_KEY,
                    secret_key=SCALEWAY_SECRET_KEY,
                    endpoint_url=SCALEWAY_ENDPOINT_URL,
                    bucket_name=SCALEWAY_BUCKET
                )
                self.storage_client = ScalewayJSONStorage(config=scaleway_config)
                self.logger.info("Initialized Scaleway JSON Storage client")
            except Exception as e:
                self.logger.error(f"Failed to initialize Scaleway JSON Storage client: {str(e)}")
                self.use_object_store = False

    def collect_weather_data(self, locations: list[Location]) -> list[dict[str, Any]]:
        """
        Collect weather data for a list of locations

        Args:
            locations: list of Location objects

        Returns:
            list of dictionaries containing weather data for each location
        """
        self.logger.info(f"Starting weather data collection for {len(locations)} locations")
        results = []

        try:
            # Step 1: Get geocoding data for all locations at once
            self.logger.info("Geocoding locations...")
            geocoded_cities = geocode_cities(locations, self.geocoding_client)

            if not geocoded_cities:
                self.logger.error("Failed to geocode any locations")
                return results

            self.logger.info(f"Successfully geocoded {len(geocoded_cities)} locations")

            # Step 2: Get weather forecast data for all geocoded locations
            self.logger.info("Fetching weather forecasts...")
            weather_forecasts = fetch_weather_forecasts(geocoded_cities, self.weather_client)

            if not weather_forecasts:
                self.logger.error("Failed to fetch any weather forecasts")
                return results

            self.logger.info(f"Successfully fetched {len(weather_forecasts)} weather forecasts")

            # Step 3: Format the results and store to Scaleway if configured
            for weather_data in weather_forecasts:
                city_name = weather_data.get("city_name")
                location_metadata = weather_data.get("location_metadata")

                if city_name and location_metadata:
                    # Extract location info from the metadata
                    result = {
                        "location": {
                            "city": city_name,
                            "country": location_metadata.get("country", "Unknown"),
                            "coordinates": {
                                "lat": location_metadata.get("latitude"),
                                "lon": location_metadata.get("longitude")
                            }
                        },
                        "weather_data": {
                            key: value for key, value in weather_data.items()
                            if key not in ["location_metadata"]  # Exclude metadata from output
                        }
                    }

                    # Store to Scaleway Object Store if client is available
                    if self.use_object_store and hasattr(self, 'storage_client'):
                        try:
                            stored = self.storage_client.store_weather(city_name, result)
                            if stored:
                                self.logger.info(f"Successfully stored weather data for {city_name} in Scaleway JSON Storage")
                            else:
                                self.logger.warning(f"Failed to store weather data for {city_name} in Scaleway JSON Storage")
                        except Exception as e:
                            self.logger.error(f"Error storing weather data for {city_name}: {str(e)}")

                    results.append(result)
                    self.logger.debug(f"Processed weather data for {city_name}")

        except Exception as e:
            self.logger.error(f"Critical error during weather data collection: {str(e)}", exc_info=True)

        self.logger.info(f"Weather data collection complete. Processed {len(results)} locations successfully.")
        return results


def main(locations_file: str = None):
    """
    Main entry point for the weather data collector

    Args:
        locations_file: Path to file with locations (optional)

    Returns:
        list of weather data for each location
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Default locations file if not provided
    if not locations_file:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        locations_file = os.path.join(base_dir, "data", "dutch_cities.txt")

    # Get locations - either from specified file or default Dutch cities
    try:
        if locations_file and os.path.exists(locations_file):
            logger.info(f"Using custom locations file: {locations_file}")
            # Custom locations file handling
            locations = []
            with open(locations_file, 'r') as f:
                for line in f:
                    city_name = line.strip()
                    if city_name:
                        locations.append(Location(city_name=city_name, country="NL"))
            logger.info(f"Loaded {len(locations)} locations from {locations_file}")
        else:
            # Use the utility function to get Dutch cities
            logger.info("Using default Dutch cities list")
            locations = get_dutch_cities()
            logger.info(f"Loaded {len(locations)} Dutch cities")

    except Exception as e:
        logger.error(f"Error loading locations: {str(e)}", exc_info=True)
        # Fallback to some default locations
        logger.info("Using fallback default locations")
        locations = [
            Location(city_name="Amsterdam", country="NL"),
            Location(city_name="Rotterdam", country="NL"),
            Location(city_name="Utrecht", country="NL")
        ]

    # Collect weather data
    collector = WeatherDataCollector()
    results = collector.collect_weather_data(locations)

    # Print storage information
    if results:
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Weather data for {len(results)} cities has been collected.")
        if collector.use_object_store and hasattr(collector, 'storage_client'):
            print(f"Data stored in Scaleway Object Storage:")
            print(f"  - Bucket: {collector.storage_client.config.bucket_name}")
            print(f"  - Path: weather/{today}/")
            city_list = ", ".join([result["location"]["city"] for result in results[:5]])
            if len(results) > 5:
                city_list += f", and {len(results) - 5} more"
            print(f"  - Cities: {city_list}")
        else:
            print("Data was not stored in Scaleway (storage disabled or configuration error)")

    return results
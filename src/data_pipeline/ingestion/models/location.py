from dataclasses import dataclass
from typing import Optional

@dataclass
class Location:
    """Configuration for a location, including city name, country, and coordinates."""
    city_name: str
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @property
    def has_coordinates(self) -> bool:
        """Check if the location has valid coordinates."""
        return self.latitude is not None and self.longitude is not None

    @property
    def coordinates_dict(self) -> dict:
        """Return coordinates as a dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        } if self.has_coordinates else {}

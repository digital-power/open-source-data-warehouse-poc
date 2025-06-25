import json
import logging
from datetime import datetime
from typing import Optional, Any

import boto3
from botocore.exceptions import ClientError

from src.data_pipeline.ingestion.models.scaleway_storage import ScalewayStorageConfig

class ScalewayJSONStorage:
    """Simple client for JSON storage in Scaleway Object Storage."""

    def __init__(self, config: ScalewayStorageConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.client = boto3.client(
            's3',
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            endpoint_url=config.endpoint_url
        )

    def store(self, data: dict[str, Any], key: str) -> bool:
        """Store JSON data."""
        try:
            self.client.put_object(
                Bucket=self.config.bucket_name,
                Key=key,
                Body=json.dumps(data, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            return True
        except ClientError as e:
            self.logger.error(f"Error storing data: {e}")
            return False

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get JSON data."""
        try:
            response = self.client.get_object(Bucket=self.config.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except (ClientError, json.JSONDecodeError) as e:
            self.logger.error(f"Error getting data: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete JSON data."""
        try:
            self.client.delete_object(Bucket=self.config.bucket_name, Key=key)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting data: {e}")
            return False

    def list(self, prefix: str = "") -> list:
        """List objects with optional prefix."""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            self.logger.error(f"Error listing objects: {e}")
            return []

    def store_weather(self, city: str, data: dict[str, Any]) -> bool:
        """Store weather data for a city."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"weather/{today}/{city.lower().replace(' ', '_')}.json"
        return self.store(data, key)

    def get_weather(self, city: str, date: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Get weather data for a city."""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        key = f"weather/{date}/{city.lower().replace(' ', '_')}.json"
        return self.get(key)
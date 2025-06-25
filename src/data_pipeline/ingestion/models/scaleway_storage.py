from dataclasses import dataclass

@dataclass
class ScalewayStorageConfig:
    """
    Configuration for Scaleway Storage.
    """
    access_key: str
    secret_key: str
    bucket_name: str
    endpoint_url: str

    def __post_init__(self):
        if not self.access_key or not self.secret_key or not self.bucket_name:
            raise ValueError("All fields must be provided and non-empty.")
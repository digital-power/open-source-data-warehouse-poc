from dataclasses import dataclass

@dataclass
class ClickhouseServerConfig:
    """Configuration for a ClickHouse server"""
    host: str
    username: str
    password: str
    port: int = 8123
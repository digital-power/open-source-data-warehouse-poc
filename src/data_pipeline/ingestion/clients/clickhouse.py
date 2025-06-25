from clickhouse_connect.driver.summary import QuerySummary

from src.data_pipeline.ingestion.models.clickhouse import ClickhouseServerConfig
import pandas as pd
import clickhouse_connect
import logging

logger = logging.getLogger(__name__)

"""Client for managing Clickhouse database operations."""
class ClickhouseClient:
    def __init__(self, config: ClickhouseServerConfig):
        """
        Initialize Clickhouse client for database operations.

        Args:
            config (ClickhouseServerConfig): Configuration object containing Clickhouse server details.
        """
        self.client = clickhouse_connect.get_client(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password
        )

    def save_dataframe(self, table_name: str, df: pd.DataFrame) -> QuerySummary:
        """
        Save a DataFrame to Clickhouse table.

        Args:
            table_name: Name of the table
            df: DataFrame to save

        Returns:
            Number of rows inserted
        """
        try:
            result = self.client.insert_df(table_name, df)
            return result
        except Exception as e:
            logger.error(f"Error saving DataFrame to Clickhouse: {str(e)}")
            raise

    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """
        Execute a query and return results as DataFrame.

        Args:
            query: SQL query to execute

        Returns:
            DataFrame with query results
        """
        try:
            result = self.client.query_df(query)
            return result
        except Exception as e:
            logger.error(f"Error executing Clickhouse query: {str(e)}")
            raise

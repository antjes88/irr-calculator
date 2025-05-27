from abc import ABC, abstractmethod
from google.cloud import bigquery
import model


class AbstractRepository(ABC):
    """
    An abstract base class for repository interfaces that define methods to interact with a data source.

    Subclasses of AbstractRepository are expected to implement these methods to handle data retrieval and storage.

    Methods:
        get_cashflows: Abstract method for retrieving cashflows from the repository.
        load_irrs: Abstract method for loading Internal Rate of Return (IRR) data into the repository.
    """

    @abstractmethod
    def get_cashflows(self) -> list[model.Cashflow]:
        """
        Abstract method for retrieving cashflows from the repository.

        Returns:
            A list of Cashflow objects representing the cashflows.

        Raises:
            NotImplementedError: This method should be implemented by concrete subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def load_irrs(self, entities: dict[str, model.Entity]):
        """
        Abstract method for loading Internal Rate of Return (IRR) data into the repository.

        Args:
            entities (dict): A dictionary of Entity objects for which IRR data will be loaded.
                The dictionary maps entity IDs to Entity objects.

        Raises:
            NotImplementedError: This method should be implemented by concrete subclasses.
        """
        raise NotImplementedError


class BiqQueryRepository(AbstractRepository):
    """
    A concrete implementation of the AbstractRepository for interacting with Google BigQuery.
    This repository class is designed to retrieve cashflows and load Internal Rate of Return (IRR) data into
    Google BigQuery.

    Args:
        project (str, optional): The Google Cloud project ID. If not specified, the default project is used.

    Attributes:
        client (bigquery.Client): The Google BigQuery client instance.
        cashflow_source (str): The SQL source query for cashflows.
        irr_destination (str): The destination table for IRR data.

    Methods:
        get(query: str) -> bigquery.table.RowIterator: Execute a SQL query and return the results.
        get_cashflows() -> list[model.Cashflow]: Retrieve cashflow data and convert it to Cashflow objects.
        load_table_from_json(data: list[dict], destination: str, job_config: bigquery.job.load.LoadJobConfig):
            Load data from a list of dictionaries into a BigQuery table.
        load_irrs(entities: dict[str, model.Entity]): Load IRR data from a dictionary of Entity objects.
    """

    def __init__(self, project=None):
        self.client = bigquery.Client(project=project)
        self.cashflow_source = "SELECT * FROM dm_accounting.cashflows"
        self.irr_destination = "publishing.entity_irrs"

    def get(self, query: str) -> bigquery.table.RowIterator:
        """
        Execute a SQL query and return the results as a RowIterator.

        Args:
            query (str): The SQL query to execute.

        Returns:
            bigquery.table.RowIterator: An iterator for the query results.
        """
        query_job = self.client.query(query)
        rows = query_job.result()

        return rows

    def get_cashflows(self) -> list[model.Cashflow]:
        """
        Retrieve cashflow data and convert it into a list of Cashflow objects.

        Returns:
            list[model.Cashflow]: A list of Cashflow objects representing the cashflows.
        """
        cashflows = []
        for row in self.get(self.cashflow_source):
            cashflows.append(
                model.Cashflow(
                    row.date, row.inflow, row.outflow, row.value, row.entity_name
                )
            )

        return cashflows

    def load_table_from_json(
        self,
        data: list[dict],
        destination: str,
        job_config: bigquery.job.load.LoadJobConfig,
    ):
        """
        Load data from a list of dictionaries into a BigQuery table.

        Args:
            data (list[dict]): The data to load as a list of dictionaries.
            destination (str): The destination table in BigQuery.
            job_config (bigquery.job.load.LoadJobConfig): Job configuration for the load operation.
        """
        load_job = self.client.load_table_from_json(
            data, destination, job_config=job_config
        )
        load_job.result()

    def load_irrs(self, entities: dict[str, model.Entity]):
        """
        Load IRR data from a dictionary of Entity objects into BigQuery. This method extracts IRR data from Entity
        objects and loads it into the specified BigQuery destination table.

        Args:
            entities (dict): A dictionary of Entity objects where the keys are entity IDs.
        """
        irrs = [irr.to_dict() for entity in entities.values() for irr in entity.irrs]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        self.load_table_from_json(irrs, self.irr_destination, job_config)

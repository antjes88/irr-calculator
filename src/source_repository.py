from abc import ABC, abstractmethod
from typing import List
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator

from src import model


class AbstractSourceRepository(ABC):
    """
    An abstract base class for source repository interfaces that define methods
    to interact with a source data storage from where to extract CashflowSnapshot
    Objects.

    Methods:
        get_cashflow_snapshots(self) -> List[model.CashflowSnapshot]:
            Abstract method for retrieving cashflow snapshots from the repository.
    """

    @abstractmethod
    def get_cashflow_snapshots(self) -> List[model.CashflowSnapshot]:
        """
        Abstract method for retrieving cashflow snapshots from the repository.

        Returns:
            A list of CashflowSnapshot objects representing the cashflow snapshots.
        Raises:
            NotImplementedError: This method should be implemented by concrete subclasses.
        """
        raise NotImplementedError


class BigQuerySourceRepository(AbstractSourceRepository):
    """
    Repository for accessing cashflow data from BigQuery.

    This class implements methods to retrieve cashflow snapshots from a BigQuery source.

    Args:
        client (bigquery.Client): The BigQuery client used to execute queries.
    Attributes:
        client (bigquery.Client): The BigQuery client used to execute queries.
        cashflow_source (str): SQL query string to select all cashflows from the staging table.
    Methods:
        get(query: str) -> RowIterator:
            Executes a SQL query on BigQuery and returns the result iterator.
        get_cashflow_snapshots() -> List[model.CashflowSnapshot]:
            Retrieves all cashflow snapshots from the BigQuery source and returns them
            as a list of CashflowSnapshot objects.
    """

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.cashflow_source = "SELECT * FROM tier2_staging.cashflows"

    def get(self, query: str) -> RowIterator:
        """
        Executes a SQL query and returns the result as a RowIterator.

        Args:
            query (str): The SQL query string to execute.
        Returns:
            RowIterator: An iterator over the rows returned by the query.
        """
        query_job = self.client.query(query)

        return query_job.result()

    def get_cashflow_snapshots(self) -> List[model.CashflowSnapshot]:
        """
        Retrieves a list of cashflow snapshot objects from the cashflow source.

        Iterates over the rows obtained from the cashflow source and constructs
        a list of `model.CashflowSnapshot` instances, each representing a snapshot
        of cashflow data for a specific date and entity.

        Returns:
            List[model.CashflowSnapshot]:
                A list of cashflow snapshot objects containing date, inflow, outflow,
                value, and entity name information.
        """
        cashflow_snapshots = []
        for row in self.get(self.cashflow_source):
            cashflow_snapshots.append(
                model.CashflowSnapshot(
                    first_day_of_month=row.first_day_of_month,
                    cumulative_inflow=row.inflow,
                    cumulative_outflow=row.outflow,
                    valuation=row.value,
                    account_name=row.entity_name,
                )
            )

        return cashflow_snapshots

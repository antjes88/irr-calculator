from abc import ABC, abstractmethod
from typing import Dict, List
from google.cloud import bigquery
import math

from src import model


class AbstractDestinationRepository(ABC):
    """
    An abstract base class for destination repository interfaces that define methods to interact with a
    destination data storage in relation to Internal Rate of Return (IRR) data.

    Methods:
        load_irrs(self, accounts: Dict[str, model.Account]):
            Abstract method for loading Internal Rate of Return (IRR) data into the repository.
    """

    @abstractmethod
    def load_irrs(self, accounts: Dict[str, model.Account]):
        """
        Abstract method for loading Internal Rate of Return (IRR) data into the repository.

        Args:
            accounts (Dict[str, model.Account]):
                A dictionary with the accounts for which IRR data will be loaded.
        Raises:
            NotImplementedError: This method should be implemented by concrete subclasses.
        """
        raise NotImplementedError


class BigQueryDestinationRepository(AbstractDestinationRepository):
    """
    Repository for loading data into BigQuery destinations.
    This class provides methods to load JSON data into BigQuery tables,
    specifically for IRR (Internal Rate of Return) snapshots associated with accounts.

    Args:
        client (bigquery.Client): The BigQuery client used for data operations.
    Attributes:
        client (bigquery.Client): The BigQuery client instance.
        irr_destination (str): The destination table for IRR snapshots.
    Methods:
        load_table_from_json(data, destination, job_config):
            Loads a list of dictionaries as JSON into the specified BigQuery table.
        load_irrs(accounts):
            Loads IRR snapshots from a dictionary of Account objects into the IRR destination table.
    """

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.irr_destination = "tier3_domain.entity_irrs"

    def load_table_from_json(
        self,
        data: List[Dict],
        destination: str,
        job_config: bigquery.LoadJobConfig,
    ):
        """
        Loads data from a JSON-like list of dictionaries into a BigQuery table.

        Args:
            data (List[Dict]): The data to be loaded, represented as a list of dictionaries.
            destination (str): The destination BigQuery table identifier in the format 'project.dataset.table'.
            job_config (bigquery.LoadJobConfig): The configuration for the load job.
        """
        load_job = self.client.load_table_from_json(
            data, destination, job_config=job_config
        )
        load_job.result()

    def load_irrs(self, accounts: dict[str, model.Account]):
        """
        Loads IRR (Internal Rate of Return) snapshots from the provided accounts into the destination table.

        Args:
            accounts (dict[str, model.Account]):
                A dictionary mapping account identifiers to Account objects, each containing IRR snapshots.
        """

        irrs = [
            {
                "first_day_of_month": irr.first_day_of_month.strftime("%Y-%m-%d"),
                "irr_monthly": irr.irr_monthly,
                "irr_annual": irr.irr_annual,
                "entity_name": irr.account_name,
            }
            for account in accounts.values()
            for irr in account.irr_snapshots
            if irr.irr_monthly is not None
            and not math.isnan(irr.irr_monthly)
            and irr.irr_annual is not None
            and not math.isnan(irr.irr_annual)
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        self.load_table_from_json(irrs, self.irr_destination, job_config)

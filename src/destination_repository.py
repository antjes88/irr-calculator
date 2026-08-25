from abc import ABC, abstractmethod
from typing import Dict, List
from google.cloud import bigquery
import math

from src import model


class AbstractDestinationRepository(ABC):

    @abstractmethod
    def load_irrs(self, accounts: Dict[str, model.Account]) -> None:

        raise NotImplementedError


class BigQueryDestinationRepository(AbstractDestinationRepository):

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.irr_destination = "tier3_domain.entity_irrs"

    def load_table_from_json(
        self,
        data: List[Dict],
        destination: str,
        job_config: bigquery.LoadJobConfig,
    ) -> None:

        load_job = self.client.load_table_from_json(
            data, destination, job_config=job_config
        )
        load_job.result()

    def load_irrs(self, accounts: dict[str, model.Account]) -> None:

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

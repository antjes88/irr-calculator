from abc import ABC, abstractmethod
from typing import Dict, List
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator

from src import model


class AbstractSourceRepository(ABC):

    @abstractmethod
    def get_accounts(self) -> Dict[str, model.Account]:

        raise NotImplementedError


class BigQuerySourceRepository(AbstractSourceRepository):

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.cashflow_source = "SELECT * FROM tier2_staging.cashflows"

    def get(self, query: str) -> RowIterator:
        query_job = self.client.query(query)

        return query_job.result()

    def _get_cashflow_snapshots(self) -> List[model.CashflowSnapshot]:

        return [
            model.CashflowSnapshot(
                first_day_of_month=row.first_day_of_month,
                cumulative_inflow=row.inflow,
                cumulative_outflow=row.outflow,
                valuation=row.value,
                account_name=row.entity_name,
            )
            for row in self.get(self.cashflow_source)
        ]

    def get_accounts(self) -> Dict[str, model.Account]:

        cashflow_snapshots = self._get_cashflow_snapshots()
        accounts: Dict[str, model.Account] = {}
        for snapshot in cashflow_snapshots:
            if snapshot.account_name not in accounts:
                accounts[snapshot.account_name] = model.Account(snapshot.account_name)
            accounts[snapshot.account_name].add_cashflow(snapshot)

        return accounts

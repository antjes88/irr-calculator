from tests.data.constants import CAHSFLOW_SNAPSHOTS
from src import source_repository


def test_get_cashflow_snapshots(
    source_repository_with_cashflows: source_repository.BigQuerySourceRepository,
):
    """
    GIVEN a repository and a collection of CashflowSnapshot objects
    WHEN they are passed as arguments to BiqQueryRepository.load_exchange_rates()
    THEN Exchange Rates should be loaded into the destination table in the data repository
    """
    results = source_repository_with_cashflows.get_cashflow_snapshots()

    assert len(results) == len(CAHSFLOW_SNAPSHOTS)
    assert sorted(results) == sorted(CAHSFLOW_SNAPSHOTS)

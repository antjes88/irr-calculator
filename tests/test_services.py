import os
import datetime as dt
import logging
from unittest.mock import MagicMock

from src.destination_repository import BigQueryDestinationRepository
from src.source_repository import BigQuerySourceRepository
from src import model, services
from tests.data.constants import ACCOUNTS


def test_irr_pipeline(
    source_repository_with_cashflows: BigQuerySourceRepository,
    bq_destination_repository: BigQueryDestinationRepository,
):
    """
    GIVEN some cashflows on bq
    WHEN they are processed by irr_pipeline() service
    THEN the expected results should be populated into the correct destination table
    """
    services.irr_pipeline(source_repository_with_cashflows, bq_destination_repository)

    for key in ACCOUNTS.keys():
        query_job = bq_destination_repository.client.query(
            f"SELECT * FROM {bq_destination_repository.irr_destination}"
            " WHERE entity_name = '{key}' ORDER BY first_day_of_month"
        )
        for row, irr_snapshot in zip(query_job.result(), ACCOUNTS[key].irr_snapshots):
            assert row["entity_name"] == irr_snapshot.account_name
            assert row["first_day_of_month"] == irr_snapshot.first_day_of_month
            assert row["irr_monthly"] == irr_snapshot.irr_monthly


def test_irr_pipeline_logs_when_not_enough_values(caplog):
    """
    GIVEN an account with fewer than 2 cashflow snapshots
    WHEN irr_pipeline is executed
    THEN it should log an info message indicating not enough values
    """
    account = model.Account("Insufficient Account")
    account.add_cashflow(
        model.CashflowSnapshot(
            dt.date(2022, 1, 1), 1000, 0, 1000, "Insufficient Account"
        )
    )

    mock_source_repo = MagicMock()
    mock_source_repo.get_accounts.return_value = {"Insufficient Account": account}
    mock_destination_repo = MagicMock()

    with caplog.at_level(logging.INFO):
        services.irr_pipeline(mock_source_repo, mock_destination_repo)

    assert "Not enough values for Insufficient Account" in caplog.text
    mock_destination_repo.load_irrs.assert_called_once_with(
        {"Insufficient Account": account}
    )

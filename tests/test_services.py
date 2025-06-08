import os
import datetime as dt

from src.destination_repository import BigQueryDestinationRepository
from src.source_repository import BigQuerySourceRepository
from src import services
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

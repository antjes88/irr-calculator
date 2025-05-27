import pytest
from src.repository import BiqQueryRepository
import os
from tests.data.cashflows import CASHFLOWS
from google.cloud import bigquery


@pytest.fixture(scope="session")
def bq_repository():
    """
    Fixture that returns instance of BiqQueryRepository()

    Returns:
        instance of BiqQueryRepository()
    """
    bq_repository = BiqQueryRepository(project=os.environ["PROJECT"])
    bq_repository.cashflow_source = (
        f"SELECT * FROM {os.environ['DATASET']}.{os.environ['SOURCE_TABLE']}"
    )
    bq_repository.irr_destination = (
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )

    return bq_repository


@pytest.fixture(scope="function")
def repository_with_cashflows(bq_repository):
    """
    Fixture that creates a cashflow table on destination BigQuery project. Also load data into table.

    Args:
        bq_repository: instance of BiqQueryRepository()

    Returns:
        instance of BiqQueryRepository() where a cashflow table has been created
    """
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    if not os.environ.get("SA_JSON"):
        bq_repository.client.create_dataset(os.environ["DATASET"], exists_ok=True)
    bq_repository.load_table_from_json(
        CASHFLOWS, os.environ["DATASET"] + "." + os.environ["SOURCE_TABLE"], job_config
    )

    yield bq_repository

    bq_repository.client.delete_table(
        os.environ["DATASET"] + "." + os.environ["SOURCE_TABLE"]
    )
    bq_repository.client.delete_table(
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )

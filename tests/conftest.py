import pytest
import os
from google.cloud import bigquery
from typing import Generator

from tests.data.constants import CASHFLOWS_DICTS
from src.utils.gcp_clients import create_bigquery_client
from src.source_repository import BigQuerySourceRepository
from src.destination_repository import BigQueryDestinationRepository


@pytest.fixture(scope="session")
def bq_source_repository() -> BigQuerySourceRepository:
    """
    Fixture that returns instance of BiqQuerySourceRepository()

    Returns:
        instance of BiqQuerySourceRepository()
    """
    client = create_bigquery_client(project_id=os.environ["PROJECT_SOURCE"])
    bq_source_repository = BigQuerySourceRepository(client=client)
    bq_source_repository.cashflow_source = (
        f"SELECT * FROM {os.environ['DATASET']}.{os.environ['SOURCE_TABLE']}"
    )

    return bq_source_repository


@pytest.fixture(scope="function")
def source_repository_with_cashflows(
    bq_source_repository: BigQuerySourceRepository,
) -> Generator[BigQuerySourceRepository, None, None]:
    """
    Fixture that creates a cashflow table on source BigQuery repository.
    Also load data into table.

    Args:
        bq_source_repository: instance of BiqQuerySourceRepository()
    Yields:
        instance of BiqQuerySourceRepository() where a cashflow table has been created
        and data loaded.
    """
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    load_job = bq_source_repository.client.load_table_from_json(
        CASHFLOWS_DICTS,
        os.environ["DATASET"] + "." + os.environ["SOURCE_TABLE"],
        job_config=job_config,
    )
    load_job.result()

    yield bq_source_repository

    bq_source_repository.client.delete_table(
        os.environ["DATASET"] + "." + os.environ["SOURCE_TABLE"]
    )


@pytest.fixture(scope="function")
def bq_destination_repository() -> Generator[BigQueryDestinationRepository, None, None]:
    """
    Fixture that returns instance of BiqQueryDestinationRepository()

    Yields:
        instance of BiqQueryDestinationRepository()
    """
    client = create_bigquery_client(project_id=os.environ["PROJECT_DESTINATION"])
    bq_destination_repository = BigQueryDestinationRepository(client=client)
    bq_destination_repository.irr_destination = (
        f"{os.environ['DATASET']}.{os.environ['DESTINATION_TABLE']}"
    )

    yield bq_destination_repository

    bq_destination_repository.client.delete_table(
        bq_destination_repository.irr_destination
    )

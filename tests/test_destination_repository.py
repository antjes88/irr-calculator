from google.cloud import bigquery

from src.destination_repository import BigQueryDestinationRepository
from tests.data.constants import ACCOUNTS


def test_load_table_from_json_actual_bq(
    bq_destination_repository: BigQueryDestinationRepository,
):
    """
    GIVEN a BigQueryDestinationRepository instance and a list of
          JSON-like dictionaries as data,
    WHEN the load_table_from_json method is called with the data,
         destination table, and job configuration,
    THEN the data should be loaded into the specified BigQuery table,
         and querying the table should return rows matching the original data.
    """
    inputs = [
        {"key1": "value1", "key2": "value2", "key3": "value3"},
        {"key1": "value11", "key2": "value22", "key3": "value33"},
        {"key1": "value111", "key2": "value222", "key3": "value333"},
    ]
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    bq_destination_repository.load_table_from_json(
        inputs, bq_destination_repository.irr_destination, job_config
    )

    query_job = bq_destination_repository.client.query(
        f"SELECT * FROM {bq_destination_repository.irr_destination}"
    )
    for row, input in zip(query_job.result(), inputs):
        for key in input:
            assert row[key] == input[key]


def test_load_irrs(
    bq_destination_repository: BigQueryDestinationRepository,
):
    """
    GIVEN a BigQueryDestinationRepository and a set of Account objects
          each with associated IrrSnapshot data,
    WHEN the load_irrs method is called with these accounts,
    THEN the IRR snapshots should be correctly loaded into the BigQuery
         destination table, and querying the table should return rows
         matching the original IrrSnapshot data for each account.
    """

    bq_destination_repository.load_irrs(ACCOUNTS)

    for key in ACCOUNTS.keys():
        query_job = bq_destination_repository.client.query(
            f"SELECT * FROM {bq_destination_repository.irr_destination}"
            " WHERE entity_name = '{key}' ORDER BY first_day_of_month"
        )
        for row, irr_snapshot in zip(query_job.result(), ACCOUNTS[key].irr_snapshots):
            assert row["entity_name"] == irr_snapshot.account_name
            assert row["first_day_of_month"] == irr_snapshot.first_day_of_month
            assert row["irr_monthly"] == irr_snapshot.irr_monthly

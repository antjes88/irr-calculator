import click
import os

from src import source_repository, destination_repository, services
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger

logger = default_module_logger(__file__)


@click.command()
def calculate_irr() -> None:
    """
    CLI entry point to execute the IRR calculation pipeline.

    Initializes BigQuery source and destination repository adapters using
    the GCP project IDs specified in the environment variables (`PROJECT_SOURCE`
    and `PROJECT_DESTINATION`) and runs the IRR data pipeline service.

    Raises:
        KeyError: If `PROJECT_SOURCE` or `PROJECT_DESTINATION` environment variables
            are not defined.
    """
    bq_source_repository = source_repository.BigQuerySourceRepository(
        client=create_bigquery_client(os.environ["PROJECT_SOURCE"]),
    )
    bq_destination_repository = destination_repository.BigQueryDestinationRepository(
        client=create_bigquery_client(os.environ["PROJECT_DESTINATION"])
    )
    logger.info("Starting IRR pipeline execution")
    services.irr_pipeline(
        source_repository=bq_source_repository,
        destination_repository=bq_destination_repository,
    )
    logger.info("Completed IRR pipeline execution")

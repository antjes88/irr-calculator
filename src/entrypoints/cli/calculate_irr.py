import click
import os

from src import source_repository, destination_repository, services, model
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger


logger = default_module_logger(__file__)


@click.command()
def calculate_irr() -> None:

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

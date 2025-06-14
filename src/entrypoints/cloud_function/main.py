from src import source_repository, destination_repository, services, model
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger


logger = default_module_logger(__file__)


def function_entry_point(event, context):
    """
    Entry point for the application. This function initializes BigQuery destination and source repositories
    connector and invokes the IRR pipeline.

    Args:
         event: The dictionary with data specific to this type of event. The `@type` field maps to
                `type.googleapis.com/google.pubsub.v1.PubsubMessage`. The `data` field maps to the PubsubMessage data
                in a base64-encoded string. The `attributes` field maps to the PubsubMessage attributes
                if any is present.
         context: Metadata of triggering event including `event_id` which maps to the PubsubMessage
                  messageId, `timestamp` which maps to the PubsubMessage publishTime, `event_type` which maps to
                  `google.pubsub.topic.publish`, and `resource` which is a dictionary that describes the service
                  API endpoint pubsub.googleapis.com, the triggering topic's name, and the triggering event type
                  `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    """
    client = create_bigquery_client()
    bq_source_repository = source_repository.BigQuerySourceRepository(
        client=client,
    )
    bq_destination_repository = destination_repository.BigQueryDestinationRepository(
        client=client,
    )
    logger.info("Starting IRR pipeline execution")
    services.irr_pipeline(
        source_repository=bq_source_repository,
        destination_repository=bq_destination_repository,
    )
    logger.info("Completed IRR pipeline execution")

from src.destination_repository import AbstractDestinationRepository
from src.source_repository import AbstractSourceRepository
from src.utils.logs import default_module_logger

logger = default_module_logger(__file__)


def irr_pipeline(
    source_repository: AbstractSourceRepository,
    destination_repository: AbstractDestinationRepository,
):

    accounts = source_repository.get_accounts()
    for account in accounts.values():
        if not account.calculate_irr():
            logger.info(f"Not enough values for {account.account_name}")

    destination_repository.load_irrs(accounts)

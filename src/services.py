from src.destination_repository import AbstractDestinationRepository
from src.source_repository import AbstractSourceRepository
from src import model


def irr_pipeline(
    source_repository: AbstractSourceRepository,
    destination_repository: AbstractDestinationRepository,
):
    """
    Executes the Internal Rate of Return (IRR) data pipeline.
    This pipeline retrieves cashflow snapshots from the source repository,
    processes them to create account collections, allocates cashflows to accounts,
    calculates IRRs for each account, and loads the resulting IRR data into the destination repository.

    Args:
        source_repository (AbstractSourceRepository): The repository used to retrieve cashflow snapshots.
        destination_repository (AbstractDestinationRepository): The repository used to store calculated IRR data.
    """
    cashflow_snapshots = source_repository.get_cashflow_snapshots()
    accounts = model.account_collection_creation(cashflow_snapshots)
    accounts = model.allocate_cashflow_snapshots_to_accounts(
        cashflow_snapshots, accounts
    )

    for account in accounts.values():
        account.calculate_irr()

    destination_repository.load_irrs(accounts)

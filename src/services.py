from repository import AbstractRepository
import model


def irr_pipeline(repository: AbstractRepository):
    """
    Perform an Internal Rate of Return (IRR) data pipeline. The pipeline retrieves cashflows, creates entities,
    allocates cashflows to entities, calculates IRRs, and loads IRR data into the repository.

    Args:
        repository (AbstractRepository): The repository for data retrieval and storage.
    """
    cashflows = repository.get_cashflows()
    entities = model.entities_collection_creation(cashflows)
    entities = model.allocate_cashflows_to_entities(cashflows, entities)

    for entity in entities.values():
        entity.calculate_irr()

    repository.load_irrs(entities)

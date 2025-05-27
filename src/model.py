from dataclasses import dataclass
import datetime as dt
import numpy_financial as npf


@dataclass(frozen=True)
class Cashflow:
    """
    A data class representing a cashflow entry. This class is used to store information about a cashflow,
    including the date, inflow, outflow, value, and entity name. The class is frozen to ensure immutability.

    Attributes:
        date (datetime.datetime): The date of the cashflow.
        inflow (float): The inflow amount.
        outflow (float): The outflow amount.
        value (float): The net value.
        entity_name (str): The name of the associated entity.
    """

    date: dt.datetime
    inflow: float
    outflow: float
    value: float
    entity_name: str

    def __gt__(self, other):
        if self.date is None:
            return False
        elif other.date is None:
            return True
        else:
            return self.date > other.date


@dataclass(frozen=True)
class Irr:
    """
    A data class representing Internal Rate of Return (IRR) data for a specific entity. This class is used to store
    information about IRR, including the date, monthly IRR value, and entity name. The class is frozen to ensure
    immutability.

    Attributes:
        date (datetime.datetime): The date of the IRR calculation.
        value (float): The monthly IRR value.
        entity_name (str): The name of the associated entity.
    Properties:
        value_annual (float): Calculate the annualized IRR value based on the monthly value.
    Methods:
        to_dict(): Convert the IRR data to a dictionary for serialization.
    """

    date: dt.datetime
    value: float
    entity_name: str

    @property
    def value_annual(self):
        """
        Calculate the annualized IRR value based on the monthly value.

        Returns:
            float: The annualized IRR value (rounded to 4 decimal places).
        """
        return round(((1 + self.value) ** 12) - 1, 4)

    def to_dict(self) -> dict:
        """
        Convert the IRR data to a dictionary for serialization.

        Returns:
            dict: A dictionary representation of the IRR data.
        """
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "irr_monthly": self.value,
            "irr_annual": self.value_annual,
            "entity_name": self.entity_name,
        }


class Entity:
    """
    A class representing an entity with associated cashflows and calculated Internal Rate of Return (IRR) data.

    Args:
        entity_name (str): The name of the entity.
    Attributes:
        entity_name (str): The name of the entity.
        sorted_cashflows (list[Cashflow]): A list of sorted Cashflow objects for the entity.
        irrs (list[Irr]): A list of calculated IRR data.
    Methods:
        add_cashflow(cashflow: Cashflow): Add a Cashflow to the entity's list of cashflows.
        calculate_irr(): Calculate IRR data based on the entity's cashflows.
    """

    def __init__(self, entity_name: str):
        self.entity_name: str = entity_name
        self.sorted_cashflows: list[Cashflow] = []
        self.irrs: list[Irr] = []

    def add_cashflow(self, cashflow: Cashflow):
        """
        Add a Cashflow to the entity's list of cashflows and ensure the list remains sorted by date.

        Args:
            cashflow (Cashflow): The Cashflow to add.
        """
        self.sorted_cashflows.append(cashflow)
        self.sorted_cashflows = sorted(self.sorted_cashflows)

    def calculate_irr(self):
        """
        Calculate IRR data based on the entity's sorted cashflows. This method calculates IRR based on cashflows and
        stores the results in the 'irrs' attribute.

        If there are not enough cashflows for calculation, a message is printed.
        """
        self.irrs = []
        if self.sorted_cashflows.__len__() < 2:
            print(f"Not enough values for {self.entity_name}")
            # raise Exception("Not enough values")
            # todo: make this to be logged
        else:
            periodic_cashflow = [
                self.sorted_cashflows[0].outflow - self.sorted_cashflows[0].inflow
            ]
            for cashflow in self.sorted_cashflows[1:]:
                periodic_cashflow.append(
                    cashflow.value + cashflow.outflow - cashflow.inflow
                )
                self.irrs.append(
                    Irr(
                        cashflow.date,
                        round(npf.irr(periodic_cashflow), 4),
                        self.entity_name,
                    )
                )
                periodic_cashflow[-1] = cashflow.outflow - cashflow.inflow

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.entity_name == other.entity_name

    def __hash__(self):
        return hash(self.entity_name)


def allocate_cashflows_to_entities(
    cashflows: list[Cashflow], entities: dict[str:Entity]
):
    """
    Allocate cashflows to entities based on the entity names.

    Args:
        cashflows (list[Cashflow]): A list of Cashflow objects to be allocated to entities.
        entities (dict[str, Entity]): A dictionary of entities where keys are entity names, and values are Entity
                                      objects.
    Returns:
        dict[str, Entity]: A dictionary of entities with updated cashflow data.
    """
    for cashflow in cashflows:
        entities[cashflow.entity_name].add_cashflow(cashflow)
    # todo: get an except catcher for KeyError!?

    return entities


def entities_collection_creation(cashflows: list[Cashflow]) -> dict[str:Entity]:
    """
    Create a collection of entities based on the provided list of cashflows.

    Args:
        cashflows (list[Cashflow]): A list of Cashflow objects from which entities will be created.
    Returns:
        dict[str, Entity]: A dictionary of entities with entity names as keys and corresponding Entity objects.
    """
    entities = {}
    entity_names = tuple([cashflow.entity_name for cashflow in cashflows])
    for entity_name in entity_names:
        entities[entity_name] = Entity(entity_name)

    return entities

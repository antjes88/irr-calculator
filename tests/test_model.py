from src import model
import datetime as dt
import pytest


def test_sort_for_cashflow():
    """
    GIVEN a list of elements for value object Cashflow
    WHEN this list is sorted [sorted()]
    THEN the Cashflow instances has to be sorted by date from older to newer
    """
    cashflow1 = model.Cashflow(dt.datetime(2022, 1, 1), 1000, 0, 0, "test entity")
    cashflow2 = model.Cashflow(dt.datetime(2023, 2, 1), 0, 100, 1000, "test entity")
    cashflow3 = model.Cashflow(dt.datetime(1998, 3, 1), 0, 100, 1000, "test entity")

    assert sorted([cashflow1, cashflow2, cashflow3]) == [
        cashflow3,
        cashflow1,
        cashflow2,
    ]


def test_sort_for_cashflow_none_cases():
    """
    GIVEN a collection of cashflows which one has None as date
    WHEN those cashflows are sorted
    THEN cashflow with None as date should be listed first
    """
    cashflow1 = model.Cashflow(None, 1000, 0, 0, "test entity")
    cashflow2 = model.Cashflow(dt.datetime(2023, 2, 1), 0, 100, 1000, "test entity")

    assert sorted([cashflow1, cashflow2]) == [cashflow1, cashflow2]
    assert sorted([cashflow2, cashflow1]) == [cashflow1, cashflow2]


def test_allocate():
    """
    GIVEN an entity
    WHEN cashflows are added to entity (Entity.add_cashflow())
    THEN cashflow collection of entity object (Entity.sorted_cashflows) are updated to include
         this cashflow and are sorted
    """
    entity_name = "test entity"
    cashflow1 = model.Cashflow(dt.datetime(2022, 1, 1), 100, 100, 100, entity_name)
    cashflow2 = model.Cashflow(dt.datetime(2023, 1, 2), 1000, 1000, 1000, entity_name)
    entity = model.Entity(entity_name)
    entities = {entity_name: entity}

    model.allocate_cashflows_to_entities([cashflow2, cashflow1], entities)

    assert entity.sorted_cashflows == [cashflow1, cashflow2]


def test_calculate_irrs():
    """
    GIVEN an entity with a collection of cashflows
    WHEN Internal Rate of Return (irr or dcf, Discounted Cash Flow) is calculated (Entity.calculate_irr())
    THEN irrs has to be calculated producing expected results
    """
    entity_name = "test account"
    entity = model.Entity(entity_name)
    entities = {entity_name: entity}

    model.allocate_cashflows_to_entities(
        [
            model.Cashflow(dt.datetime(2022, 1, 1), 1000, 0, 0, entity_name),
            model.Cashflow(dt.datetime(2022, 2, 1), 0, 100, 1000, entity_name),
            model.Cashflow(dt.datetime(2022, 3, 1), 0, 100, 1000, entity_name),
        ],
        entities,
    )

    entities[entity_name].calculate_irr()

    assert entities[entity_name].irrs == [
        model.Irr(dt.datetime(2022, 2, 1), 0.1, entity_name),
        model.Irr(dt.datetime(2022, 3, 1), 0.1, entity_name),
    ]


@pytest.mark.parametrize(
    "value, expected_result", [(1, 4095), (-1, -1), (0.01, 0.1268)]
)
def test_cashflow_value_annual(value, expected_result):
    """
    GIVEN an Internal Rate of Return with a monthly value
    WHEN calling Irr.value_annual
    THEN the annualised irr value has to be returned
    """
    irr = model.Irr(dt.datetime(2022, 2, 1), value, "test - account")

    assert irr.value_annual == expected_result


def test_irr_to_dict():
    """
    GIVEN an Internal Rate of Return
    WHEN it is converted to dict
    THEN check that the return is the expected value
    """
    irr = model.Irr(dt.datetime(2022, 2, 1), 1, "test - account")

    assert irr.to_dict() == {
        "date": "2022-02-01",
        "irr_monthly": 1,
        "irr_annual": 4095,
        "entity_name": "test - account",
    }


def test_entity_equality():
    """
    GIVEN 2 entities
    WHEN they have the same entity name
    THEN they are equal
    """
    entity_name = "test entity"
    entity1 = model.Entity(entity_name)
    entity2 = model.Entity(entity_name)

    assert entity1 == entity2


def test_entity_inequality():
    """
    GIVEN 2 entities
    WHEN they have different entity name
    THEN they are different
    """
    entity1 = model.Entity("test entity")
    entity2 = model.Entity("other")

    assert not entity1 == entity2
    assert not entity1 == 1

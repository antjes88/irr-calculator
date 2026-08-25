from src import model
import datetime as dt
import pytest


def test_sort_for_cashflow():
    """
    GIVEN a list of elements for value object Cashflow
    WHEN this list is sorted [sorted()]
    THEN the Cashflow instances has to be sorted by date from older to newer
    """
    cashflow1 = model.CashflowSnapshot(
        dt.datetime(2022, 1, 1), 1000, 0, 0, "test entity"
    )
    cashflow2 = model.CashflowSnapshot(
        dt.datetime(2023, 2, 1), 0, 100, 1000, "test entity"
    )
    cashflow3 = model.CashflowSnapshot(
        dt.datetime(1998, 3, 1), 0, 100, 1000, "test entity"
    )

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
    cashflow1 = model.CashflowSnapshot(
        dt.datetime(1990, 1, 1), 1000, 0, 0, "test entity"
    )
    cashflow2 = model.CashflowSnapshot(
        dt.datetime(2023, 2, 1), 0, 100, 1000, "test entity"
    )

    assert sorted([cashflow1, cashflow2]) == [cashflow1, cashflow2]
    assert sorted([cashflow2, cashflow1]) == [cashflow1, cashflow2]


@pytest.mark.parametrize(
    "date1, date2, expected_result",
    [
        (dt.date(2023, 1, 1), dt.date(2022, 1, 1), True),
        (dt.date(2022, 1, 1), dt.date(2023, 1, 1), False),
        (dt.date(2022, 1, 1), dt.date(2022, 1, 1), False),
        (None, dt.date(2022, 1, 1), False),
        (dt.date(2022, 1, 1), None, True),
        (None, None, False),
    ],
)
def test_cashflow_snapshot_gt(date1, date2, expected_result):
    """
    GIVEN two CashflowSnapshot instances with various dates (including None)
    WHEN comparing them with the greater-than operator (>)
    THEN it should evaluate to the expected boolean result
    """
    snapshot1 = model.CashflowSnapshot(date1, 1000, 0, 0, "entity 1")
    snapshot2 = model.CashflowSnapshot(date2, 2000, 100, 500, "entity 2")

    assert (snapshot1 > snapshot2) == expected_result
    assert snapshot1.__gt__(snapshot2) == expected_result


def test_calculate_irrs_insufficient_values():
    """
    GIVEN an entity with fewer than 2 cashflows
    WHEN calculate_irr() is called
    THEN it should return False and irr_snapshots should be empty
    """
    account = model.Account("test account")
    account.add_cashflow(
        model.CashflowSnapshot(dt.datetime(2022, 1, 1), 1000, 0, 0, "test account")
    )

    assert account.calculate_irr() is False
    assert account.irr_snapshots == []


@pytest.mark.parametrize(
    "value, expected_result", [(1, 4095), (-1, -1), (0.01, 0.1268)]
)
def test_cashflow_value_annual(value, expected_result):
    """
    GIVEN an Internal Rate of Return with a monthly value
    WHEN calling Irr.value_annual
    THEN the annualised irr value has to be returned
    """
    irr = model.IrrSnapshot(dt.datetime(2022, 2, 1), value, "test - account")

    assert irr.irr_annual == expected_result


@pytest.mark.parametrize(
    "name1, name2, expected_equal",
    [
        ("Account A", "Account A", True),
        ("Account A", "Account B", False),
        ("account a", "Account A", False),
        ("", "", True),
        ("", "Account", False),
        ("Test #123", "Test #123", True),
    ],
)
def test_account_equality_and_hash(name1, name2, expected_equal):
    """
    GIVEN two Account instances with various names
    WHEN comparing them with == and computing their hashes
    THEN equality, hash consistency, and set deduplication should match expectation
    """
    account1 = model.Account(name1)
    account2 = model.Account(name2)

    assert (account1 == account2) == expected_equal
    assert (hash(account1) == hash(account2)) == expected_equal

    if expected_equal:
        assert len({account1, account2}) == 1
    else:
        assert len({account1, account2}) == 2


def test_account_equality_non_account_type():
    """
    GIVEN an Account instance and non-Account objects
    WHEN comparing them with ==
    THEN it should return False
    """
    account = model.Account("test entity")

    assert not (account == 1)
    assert not (account == "test entity")
    assert not (account is None)

import datetime as dt
from typing import List

from src import model


CASHFLOWS_DICTS = [
    {
        "first_day_of_month": "2022-01-01",
        "inflow": 1000,
        "outflow": 0,
        "value": 1000,
        "entity_name": "Test Account 1",
    },
    {
        "first_day_of_month": "2022-02-01",
        "inflow": 0,
        "outflow": 100,
        "value": 1000,
        "entity_name": "Test Account 1",
    },
    {
        "first_day_of_month": "2022-03-01",
        "inflow": 0,
        "outflow": 100,
        "value": 1000,
        "entity_name": "Test Account 1",
    },
    {
        "first_day_of_month": "2022-04-01",
        "inflow": 0,
        "outflow": 100,
        "value": 1000,
        "entity_name": "Test Account 1",
    },
    {
        "first_day_of_month": "2022-05-01",
        "inflow": 0,
        "outflow": 100,
        "value": 1000,
        "entity_name": "Test Account 1",
    },
    {
        "first_day_of_month": "2022-03-01",
        "inflow": 1000,
        "outflow": 0,
        "value": 1000,
        "entity_name": "Test Account 2",
    },
    {
        "first_day_of_month": "2022-04-01",
        "inflow": 0,
        "outflow": 0,
        "value": 1100,
        "entity_name": "Test Account 2",
    },
]

CAHSFLOW_SNAPSHOTS: List[model.CashflowSnapshot] = []
for cashflow in CASHFLOWS_DICTS:
    CAHSFLOW_SNAPSHOTS.append(
        model.CashflowSnapshot(
            first_day_of_month=dt.datetime.strptime(
                cashflow["first_day_of_month"], "%Y-%m-%d"
            ).date(),
            cumulative_inflow=cashflow["inflow"],
            cumulative_outflow=cashflow["outflow"],
            valuation=cashflow["value"],
            account_name=cashflow["entity_name"],
        )
    )

ACCOUNT1 = model.Account("Test Account 1")
ACCOUNT1.irr_snapshots = [
    model.IrrSnapshot(
        first_day_of_month=dt.date(2022, 2, 1),
        irr_monthly=0.1,
        account_name="Test Account 1",
    ),
    model.IrrSnapshot(
        first_day_of_month=dt.date(2022, 3, 1),
        irr_monthly=0.1,
        account_name="Test Account 1",
    ),
    model.IrrSnapshot(
        first_day_of_month=dt.date(2022, 4, 1),
        irr_monthly=0.1,
        account_name="Test Account 1",
    ),
    model.IrrSnapshot(
        first_day_of_month=dt.date(2022, 5, 1),
        irr_monthly=0.1,
        account_name="Test Account 1",
    ),
]

ACCOUNT2 = model.Account("Test Account 2")
ACCOUNT2.irr_snapshots = [
    model.IrrSnapshot(
        first_day_of_month=dt.date(2022, 4, 1),
        irr_monthly=0.1,
        account_name="Test Account 2",
    )
]
ACCOUNTS = {"Test Account 1": ACCOUNT1, "Test Account 2": ACCOUNT2}

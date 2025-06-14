from dataclasses import dataclass
import datetime as dt
import numpy_financial as npf
from typing import List, Dict
from src.utils.logs import default_module_logger


logger = default_module_logger(__file__)


@dataclass(frozen=True)
class CashflowSnapshot:
    """
    Represents a snapshot of an account's financial position at a specific date.

    Attributes:
        first_day_of_month (datetime): The date of the snapshot.
        cumulative_inflow (float): Total cash received up to this date.
        cumulative_outflow (float): Total cash spent up to this date.
        valuation (float): The current estimated value of the account at this date.
        account_name (str): The name of the account being tracked.
    """

    first_day_of_month: dt.date
    cumulative_inflow: float
    cumulative_outflow: float
    valuation: float
    account_name: str

    def __gt__(self, other: "CashflowSnapshot") -> bool:
        if self.first_day_of_month is None:
            return False
        elif other.first_day_of_month is None:
            return True
        else:
            return self.first_day_of_month > other.first_day_of_month


@dataclass(frozen=True)
class IrrSnapshot:
    """
    Represents the internal rate of return (IRR) snapshot for a given account on a specific date.

    Attributes:
        first_day_of_month (datetime): The date of the IRR calculation.
        irr_monthly (float): Monthly IRR value as a decimal (e.g., 0.02 for 2%).
        account_name (str): The name of the associated account.

    Properties:
        irr_annual (float): The annualized IRR value based on the monthly IRR.
    """

    first_day_of_month: dt.date
    irr_monthly: float
    account_name: str

    @property
    def irr_annual(self) -> float:
        """
        Compute the annualized IRR using monthly compounding.

        Returns:
            float: The annualized IRR value (rounded to 4 decimal places).
        """
        return round(((1 + self.irr_monthly) ** 12) - 1, 4)


class Account:
    """
    Represents a financial account that manages cashflow snapshots and calculates
    Internal Rate of Return (IRR) over time.

    Args:
        account_name (str): The name identifying this financial account.
    Attributes:
        account_name (str): The name of the account.
        sorted_cashflow_snapshots (List[CashflowSnapshot]):
            Chronologically ordered cashflow snapshots associated with this account.
        irr_snapshots (List[IrrSnapshot]):
            Calculated IRR values derived from the cashflow snapshots.
    Methods:
        add_cashflow(cashflow_snapshot: CashflowSnapshot):
            Adds a cashflow snapshot and keeps the internal list sorted by date.
        calculate_irr():
            Computes IRR snapshots from the list of sorted cashflows.
    """

    def __init__(self, account_name: str):
        self.account_name: str = account_name
        self.sorted_cashflow_snapshots: list[CashflowSnapshot] = []
        self.irr_snapshots: list[IrrSnapshot] = []

    def add_cashflow(self, cashflow_snapshot: CashflowSnapshot):
        """
        Add a CashflowSnapshot to the account's list of cashflow snapshots and ensure
        the list remains sorted by date.

        Args:
            cashflow_snapshot (CashflowSnapshot): The CashflowSnapshot to add.
        """
        self.sorted_cashflow_snapshots.append(cashflow_snapshot)
        self.sorted_cashflow_snapshots = sorted(self.sorted_cashflow_snapshots)

    def calculate_irr(self):
        """
        Calculates the IRR snapshots based on the chronological cashflows.

        This method builds a list of periodic cashflows and computes the IRR
        at each point using NumPy's financial IRR function. The resulting
        IRR values are stored as IrrSnapshot instances in the `irr_snapshots` list.

        If fewer than two cashflow snapshots exist, a warning is issued.
        """
        self.irr_snapshots = []
        if len(self.sorted_cashflow_snapshots) < 2:
            logger.info(f"Not enough values for {self.account_name}")

        else:
            periodic_cashflow = [
                self.sorted_cashflow_snapshots[0].cumulative_outflow
                - self.sorted_cashflow_snapshots[0].cumulative_inflow
            ]

            for cashflow in self.sorted_cashflow_snapshots[1:]:
                periodic_cashflow.append(
                    cashflow.valuation
                    + cashflow.cumulative_outflow
                    - cashflow.cumulative_inflow
                )
                self.irr_snapshots.append(
                    IrrSnapshot(
                        cashflow.first_day_of_month,
                        round(npf.irr(periodic_cashflow), 4),
                        self.account_name,
                    )
                )
                periodic_cashflow[-1] = (
                    cashflow.cumulative_outflow - cashflow.cumulative_inflow
                )

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.account_name == other.account_name

    def __hash__(self):
        return hash(self.account_name)


def allocate_cashflow_snapshots_to_accounts(
    cashflow_snapshots: List[CashflowSnapshot], accounts: Dict[str, Account]
) -> Dict[str, Account]:
    """
    Allocate cashflow snapshots to accounts based on the account names.

    Args:
        cashflow_snapshots (List[CashflowSnapshot]):
            A list of CashflowSnapshot objects to be allocated to accounts.
        accounts (dict[str, Account]):
            A dictionary of accounts where keys are account names, and values are Account
            objects.
    Returns:
        Dict[str, Account]: A dictionary of accounts with updated cashflow snapshots data.
    """
    for cashflow_snapshot in cashflow_snapshots:
        accounts[cashflow_snapshot.account_name].add_cashflow(cashflow_snapshot)

    return accounts


def account_collection_creation(
    cashflow_snapshots: List[CashflowSnapshot],
) -> Dict[str, Account]:
    """
    Create a collection of accounts based on the provided list of cashflow snapshots.

    Args:
        cashflow_snapshots (List[Cashflow]):
            A list of CashflowSnapshot objects from which accounts will be created.
    Returns:
        Dict[str, Account]:
            A dictionary of accounts with account names as keys and corresponding Account objects.
    """
    accounts = {}
    account_names = tuple(
        [cashflow_snapshot.account_name for cashflow_snapshot in cashflow_snapshots]
    )
    for account_name in account_names:
        accounts[account_name] = Account(account_name)

    return accounts

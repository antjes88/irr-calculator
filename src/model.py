from dataclasses import dataclass
import datetime as dt
import numpy_financial as npf


@dataclass(frozen=True)
class CashflowSnapshot:

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

    first_day_of_month: dt.date
    irr_monthly: float
    account_name: str

    @property
    def irr_annual(self) -> float:

        return round(((1 + self.irr_monthly) ** 12) - 1, 4)


class Account:

    def __init__(self, account_name: str):
        self.account_name: str = account_name
        self.sorted_cashflow_snapshots: list[CashflowSnapshot] = []
        self.irr_snapshots: list[IrrSnapshot] = []

    def add_cashflow(self, cashflow_snapshot: CashflowSnapshot) -> None:

        self.sorted_cashflow_snapshots.append(cashflow_snapshot)
        self.sorted_cashflow_snapshots = sorted(self.sorted_cashflow_snapshots)

    def calculate_irr(self) -> bool:

        self.irr_snapshots = []
        if len(self.sorted_cashflow_snapshots) < 2:
            return False

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

        return True

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.account_name == other.account_name

    def __hash__(self):
        return hash(self.account_name)

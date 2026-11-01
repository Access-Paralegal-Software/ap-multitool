"""LEDES 1998B format exporter for legal billing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class LEDES1998BRecord:
    """Represents a single fee entry in LEDES 1998B standard."""

    invoice_date: date
    invoice_number: str
    client_id: str
    matter_id: str
    timekeeper_id: str
    timekeeper_name: str
    timekeeper_classification: str  # e.g. "PL" (Paralegal), "PT" (Partner), "AS" (Associate)
    activity_date: date
    units: float
    rate: float
    description: str
    task_code: str = "L110"      # UTBMS Task code e.g. L110 Fact Investigation
    activity_code: str = "A102"  # UTBMS Activity code e.g. A102 Research

    @property
    def line_total(self) -> float:
        return round(self.units * self.rate, 2)

    def to_pipe_delimited(self) -> str:
        """Format entry as a LEDES 1998B pipe-delimited line."""
        # Standard LEDES 1998B fields:
        # INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|LAW_FIRM_MATTER_ID|INVOICE_TOTAL|
        # BILLING_START_DATE|BILLING_END_DATE|INVOICE_DESCRIPTION|LINE_ITEM_NUMBER|
        # EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|LINE_ITEM_UNIT_COST|
        # LINE_ITEM_TOTAL_AMOUNT|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|LINE_ITEM_ACTIVITY_CODE|
        # TIMEKEEPER_ID|LINE_ITEM_DESCRIPTION|LAW_FIRM_ID|LINE_ITEM_TIMEKEEPER_NAME|
        # TIMEKEEPER_CLASSIFICATION|CLIENT_MATTER_ID
        inv_dt = self.invoice_date.strftime("%Y%m%d")
        act_dt = self.activity_date.strftime("%Y%m%d")
        return (
            f"{inv_dt}|{self.invoice_number}|{self.client_id}|{self.matter_id}|"
            f"FEE|{self.units:.2f}|{self.rate:.2f}|{self.line_total:.2f}|{act_dt}|"
            f"{self.task_code}|{self.activity_code}|{self.timekeeper_id}|"
            f"{self.description}|{self.timekeeper_name}|{self.timekeeper_classification}"
        )


def generate_ledes_1998b_header() -> str:
    """Return standard LEDES 1998B file header."""
    return "INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|LAW_FIRM_MATTER_ID|EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|LINE_ITEM_UNIT_COST|LINE_ITEM_TOTAL_AMOUNT|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|LINE_ITEM_ACTIVITY_CODE|TIMEKEEPER_ID|LINE_ITEM_DESCRIPTION|LINE_ITEM_TIMEKEEPER_NAME|TIMEKEEPER_CLASSIFICATION"

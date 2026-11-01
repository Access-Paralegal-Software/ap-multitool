"""
paralegal_time.formats.formatter_1998b
Official 24-field pipe-delimited LEDES 1998B legal electronic billing generator.
Maintained strictly by Alan Woodyard.
"""

from typing import List, Dict, Any

LEDES_1998B_HEADER = (
    "INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|LAW_FIRM_MATTER_ID|INVOICE_TOTAL|"
    "BILLING_START_DATE|BILLING_END_DATE|INVOICE_DESCRIPTION|LINE_ITEM_NUMBER|"
    "EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|LINE_ITEM_ADJUSTMENT_AMOUNT|"
    "LINE_ITEM_TOTAL|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|LINE_ITEM_DESCRIPTION|"
    "LINE_ITEM_ACTIVITY_CODE|TIMEKEEPER_ID|LINE_ITEM_UNIT_COST|TIMEKEEPER_NAME|"
    "TIMEKEEPER_CLASSIFICATION|CLIENT_MATTER_ID|LAW_FIRM_ID|LINE_ITEM_EXPENSE_CODE[]"
)

def format_ledes_date(dt_str: str) -> str:
    """Ensures YYYYMMDD date format."""
    return dt_str.replace("-", "").replace("/", "")[:8]

def generate_ledes_1998b(invoice_meta: Dict[str, Any], line_items: List[Dict[str, Any]]) -> str:
    """
    Generates compliant LEDES 1998B pipe-delimited file.
    Every line ends with [] bracket terminator.
    """
    lines = ["LEDES1998B[]", LEDES_1998B_HEADER]

    inv_date = format_ledes_date(invoice_meta.get("invoice_date", "20261001"))
    inv_num = str(invoice_meta.get("invoice_number", "INV-001"))
    client_id = str(invoice_meta.get("client_id", "CLIENT-01"))
    matter_id = str(invoice_meta.get("matter_id", "MATTER-01"))
    start_date = format_ledes_date(invoice_meta.get("billing_start", inv_date))
    end_date = format_ledes_date(invoice_meta.get("billing_end", inv_date))
    inv_desc = invoice_meta.get("description", "Legal Services Rendered")
    firm_id = str(invoice_meta.get("law_firm_id", "FIRM-01"))
    client_matter_id = str(invoice_meta.get("client_matter_id", matter_id))

    total_amount = sum(float(item.get("total_cents", 0)) / 100.0 for item in line_items)
    inv_total_str = f"{total_amount:.2f}"

    for idx, item in enumerate(line_items, 1):
        line_num = str(item.get("line_number", idx))
        item_type = item.get("type", "F")  # F = Fee, E = Expense
        billed_s = int(item.get("billed_seconds", 0))
        units = billed_s / 3600.0
        units_str = f"{units:.2f}"
        
        rate_cents = int(item.get("rate_cents", 0))
        rate_str = f"{(rate_cents / 100.0):.2f}"
        item_total_cents = int(item.get("total_cents", round(units * rate_cents)))
        item_total_str = f"{(item_total_cents / 100.0):.2f}"

        item_date = format_ledes_date(item.get("date", inv_date))
        task_code = item.get("task_code", "L110")
        act_code = item.get("activity_code", "A104")
        desc = item.get("description", "Paralegal document review").replace("|", " ").replace("\n", " ")
        tk_id = str(item.get("timekeeper_id", "TK-01"))
        tk_name = str(item.get("timekeeper_name", "Woodyard, Alan"))
        tk_class = str(item.get("timekeeper_class", "LA"))  # LA = Legal Assistant / Paralegal
        exp_code = item.get("expense_code", "")

        fields = [
            inv_date, inv_num, client_id, matter_id, inv_total_str,
            start_date, end_date, inv_desc, line_num, item_type,
            units_str, "0.00", item_total_str, item_date, task_code,
            desc, act_code, tk_id, rate_str, tk_name, tk_class,
            client_matter_id, firm_id, exp_code
        ]
        lines.append("|".join(fields) + "[]")

    return "\r\n".join(lines) + "\r\n"

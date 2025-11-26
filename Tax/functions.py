# functions.py
"""
Functions for Malaysian Tax Input Program.

Contains:
- verify_user(ic_number, password)
- calculate_tax(income, tax_relief)
- save_to_csv(data, filename)
- read_from_csv(filename)

Uses pandas for CSV read/write.
"""

import os
import pandas as pd

def verify_user(ic_number: str, password: str) -> bool:
    """
    Verify user credentials:
    - ic_number must be 12 digits (numbers only)
    - password must match last 4 digits of ic_number
    Returns True if valid, False otherwise.
    """
    # sanitize input
    if not isinstance(ic_number, str) or not isinstance(password, str):
        return False
    ic = ic_number.strip()
    pw = password.strip()
    if len(ic) != 12 or not ic.isdigit():
        return False
    return pw == ic[-4:]


def calculate_tax(income: float, tax_relief: float) -> float:
    """
    Calculate tax payable (RM) using progressive resident tax rates
    for Year of Assessment 2024 (used in 2025 filing), per official tables.

    Steps:
    - Compute chargeable_income = max(0, income - tax_relief)
    - Apply progressive bands and rates to chargeable_income
    - Return tax payable as float (rounded to 2 decimals)

    NOTE:
    - For non-residents or if you want to apply a flat rate (30%), modify this function.
    - Rates & bands used in this function are based on LHDN tables for YA 2024/2025.
    """
    try:
        income = float(income)
        tax_relief = float(tax_relief)
    except Exception:
        raise ValueError("Income and tax_relief must be numbers.")

    chargeable = income - tax_relief
    if chargeable <= 0:
        return 0.0

    # Tax bands and corresponding marginal rates
    # Each band entry: (upper_limit, marginal_rate)
    # upper_limit is cumulative upper bound for that slab (RM)
    # Based on official progressive schedule (YA 2024/2025)
    bands = [
        (5000, 0.00),
        (20000, 0.01),
        (35000, 0.03),
        (50000, 0.06),
        (70000, 0.11),
        (100000, 0.19),
        (400000, 0.25),
        (600000, 0.26),
        (2000000, 0.28),  # up to 2,000,000
        (float('inf'), 0.30)
    ]

    tax = 0.0
    lower = 0.0
    remaining = chargeable

    for upper, rate in bands:
        slab_width = upper - lower
        if chargeable > lower:
            taxable_in_slab = min(chargeable, upper) - lower
            tax += taxable_in_slab * rate
        lower = upper
        if chargeable <= upper:
            break

    return round(tax, 2)


def save_to_csv(data: dict, filename: str):
    """
    Save user tax record to CSV using pandas.
    data: dict with keys: 'ic_number','income','tax_relief','tax_payable'
    filename: path to CSV file.
    If file doesn't exist, create with header. If exists, append.
    """
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    required_keys = ['ic_number', 'income', 'tax_relief', 'tax_payable']
    for k in required_keys:
        if k not in data:
            raise ValueError(f"data missing required key: {k}")

    df_new = pd.DataFrame([{
        'ic_number': str(data['ic_number']),
        'income': float(data['income']),
        'tax_relief': float(data['tax_relief']),
        'tax_payable': float(data['tax_payable'])
    }])

    if os.path.exists(filename):
        try:
            df_old = pd.read_csv(filename)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.to_csv(filename, index=False)
        except Exception:
            # fallback: append without reading
            df_new.to_csv(filename, mode='a', header=False, index=False)
    else:
        df_new.to_csv(filename, index=False)


def read_from_csv(filename: str):
    """
    Read CSV file and return pandas DataFrame.
    If file doesn't exist, return None.
    """
    if not os.path.exists(filename):
        return None
    try:
        df = pd.read_csv(filename)
        return df
    except Exception:
        return None 
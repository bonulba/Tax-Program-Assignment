"""
Main interactive program for Malaysian Tax Input Program.
Requires: pandas installed (used inside functions.py)
Files used:
- users.csv: to store registered IC numbers
- tax_records.csv: to store tax calculation records

Usage: python main.py
"""

import os
import getpass
import sys
from functions import verify_user, calculate_tax, save_to_csv, read_from_csv
import pandas as pd

USERS_FILE = "users.csv"
TAX_FILE = "tax_records.csv"

def register_user():
    print("== User Registration ==")
    while True:
        ic = input("Enter IC number (12 digits, numbers only): ").strip()
        if len(ic) == 12 and ic.isdigit():
            break
        print("Invalid IC. It must be 12 digits. Try again.")

    last4 = ic[-4:]
    print("Registration complete. Your login password will be the last 4 digits of your IC.")

    # Save to USERS_FILE
    user_row = {'ic_number': ic}
    if os.path.exists(USERS_FILE):
        try:
            df = pd.read_csv(USERS_FILE)
            if ic in df['ic_number'].astype(str).tolist():
                print("You are already registered.")
                return ic
            df = pd.concat([df, pd.DataFrame([user_row])], ignore_index=True)
            df.to_csv(USERS_FILE, index=False)
        except Exception:
            pd.DataFrame([user_row]).to_csv(USERS_FILE, index=False)
    else:
        pd.DataFrame([user_row]).to_csv(USERS_FILE, index=False)

    return ic

def login():
    print("== Login ==")
    if not os.path.exists(USERS_FILE) or pd.read_csv(USERS_FILE).empty:
        print("No registered users found. Please register first.")
        ic = register_user()
        print("Now login using your IC and password (last 4 digits).")
    else:
        ic = input("Enter your IC number: ").strip()

    pw = getpass.getpass("Enter password (last 4 digits of IC): ").strip()
    if verify_user(ic, pw):
        print("Login successful.\n")
        return ic
    else:
        print("Invalid credentials. Exiting.")
        return None

def prompt_income_and_relief():
    while True:
        try:
            income = float(input("Enter your annual income (RM): ").strip())
            if income < 0:
                print("Income cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number for income.")
    while True:
        try:
            relief = float(input("Enter your total tax relief (RM): ").strip())
            if relief < 0:
                print("Tax relief cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number for tax relief.")
    return income, relief

def view_records():
    df = read_from_csv(TAX_FILE)
    if df is None or df.empty:
        print("No tax records found.")
        return
    print("\n== Tax Records ==")
    print(df.to_string(index=False))
    print()

def main_menu(ic):
    while True:
        print("=== Menu ===")
        print("1. Calculate tax and save record")
        print("2. View all tax records (CSV)")
        print("3. Logout / Exit")
        choice = input("Choose (1-3): ").strip()
        if choice == '1':
            income, relief = prompt_income_and_relief()
            tax = calculate_tax(income, relief)
            print(f"\nChargeable Income: RM{max(0, income-relief):,.2f}")
            print(f"Tax payable: RM{tax:,.2f}\n")
            # Save record
            data = {
                'ic_number': ic,
                'income': income,
                'tax_relief': relief,
                'tax_payable': tax
            }
            try:
                save_to_csv(data, TAX_FILE)
                print(f"Record saved to {TAX_FILE}.\n")
            except Exception as e:
                print("Error saving record:", e)
        elif choice == '2':
            view_records()
        elif choice == '3':
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1, 2, or 3.")

# ------------------------------
# Main program start
# ------------------------------
if __name__ == "__main__":
    print("=== Malaysian Tax Input Program ===")
    print("1) Login")
    print("2) Register")
    mode = input("Choose 1 or 2: ").strip()
    if mode == '2':
        ic = register_user()
        print("Proceed to login.")
        ic = login()
    else:
        ic = login()
    if ic:
        main_menu(ic)
    else:
        sys.exit(1)
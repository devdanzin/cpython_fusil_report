import pandas as pd
import numpy as np

# Load the main CSV file
df_issues = pd.read_csv("cpython_fusil_report - cpython_fusil_report.csv.csv")

# --- Data Preparation ---
# Convert date columns to datetime objects
df_issues['Date Filed'] = pd.to_datetime(df_issues['Date Filed'], format='%d/%m/%Y', errors='coerce')
df_issues['Closed Date'] = pd.to_datetime(df_issues['Closed Date'], format='%d/%m/%Y', errors='coerce')

# --- Placeholder 1: Issue counts ---
total_issues = len(df_issues)

# Standardize status for counting.
issues_open = df_issues[df_issues['Status'].str.lower() == 'open'].shape[0]
issues_closed = df_issues[df_issues['Status'].str.lower() == 'closed'].shape[0]

print(f"--- Issue Counts ---")
print(f"Total issues filled: {total_issues}")
print(f"Issues currently open (from CSV 'Status'): {issues_open}")
print(f"Issues currently closed (from CSV 'Status'): {issues_closed}")

if total_issues == (issues_open + issues_closed):
    print(f"Breakdown from CSV: {issues_open} open, {issues_closed} closed.")
else:
    # This might happen if 'Status' has other values or NaNs not handled by str.lower()
    print(f"Discrepancy or other statuses in CSV: {issues_open} open + {issues_closed} closed != {total_issues} total. Please check 'Status' column values in the CSV. Found values: {df_issues['Status'].unique()}")


# --- Placeholder 3: Number of issues by kind ---
print(f"\n--- Issues by Kind (from CSV 'Guessed Kind') ---")
issues_by_kind = df_issues['Guessed Kind'].fillna('Unknown').value_counts()
print(issues_by_kind)

# --- Placeholder 4: Number of issues by configuration ---
# Attempt to get this from 'cpython_fusil_report - Summary Table.csv' first
# as it's more likely to have a clean 'Configuration' column.
issues_by_config_source = "Not found"
df_summary = None # Initialize df_summary
try:
    df_summary = pd.read_csv("cpython_fusil_report - Summary Table.csv")
    if 'Configuration' in df_summary.columns:
        print("\n--- Issues by Configuration (from 'cpython_fusil_report - Summary Table.csv') ---")
        # Ensure we're mapping to the 52 issues if df_summary is the same length
        if len(df_summary) == total_issues:
            issues_by_config_summary = df_summary['Configuration'].fillna('Unknown').value_counts()
            print(issues_by_config_summary)
            issues_by_config_source = "'cpython_fusil_report - Summary Table.csv'"
        else:
            print(f"Warning: 'Summary Table.csv' has {len(df_summary)} rows, but main issues CSV has {total_issues} rows. Configuration data might not align directly for a simple value_counts unless 'Summary Table.csv' is an aggregated view.")
            # If lengths differ, it might be an aggregate table already.
            # Print its value counts directly if the column exists.
            print("Value counts from 'Configuration' column in 'Summary Table.csv':")
            print(df_summary['Configuration'].fillna('Unknown').value_counts())
            issues_by_config_source = "'cpython_fusil_report - Summary Table.csv' (potentially aggregated)"


    else:
        print("\n'Configuration' column not found in 'cpython_fusil_report - Summary Table.csv'.")
except FileNotFoundError:
    print("\n'cpython_fusil_report - Summary Table.csv' not found.")
    issues_by_config_source = "Not found ('Summary Table.csv' missing)"
except Exception as e:
    print(f"\nAn error occurred while loading 'cpython_fusil_report - Summary Table.csv': {e}")
    issues_by_config_source = "Error loading 'Summary Table.csv'"


if issues_by_config_source.startswith("Not found") or issues_by_config_source.startswith("Error"):
    print("As 'Configuration' was not definitively found or loaded from 'Summary Table.csv', consider using the 'Configuration' column from the Markdown table in `cpython_report.md` or manually creating this summary.")


# --- PR Counts ---
print(f"\n--- PR Counts (Analysis) ---")
print("The 'PRs (author)' column in 'cpython_fusil_report - cpython_fusil_report.csv.csv' is empty.")

# Check 'Number of PRs' in the main df_issues
if 'Number of PRs' in df_issues.columns and df_issues['Number of PRs'].notna().any():
    print("Found 'Number of PRs' in 'cpython_fusil_report - cpython_fusil_report.csv.csv'.")
    df_issues['Number of PRs num'] = pd.to_numeric(df_issues['Number of PRs'], errors='coerce')
    if df_issues['Number of PRs num'].notna().any():
        total_prs_main_csv = df_issues['Number of PRs num'].sum()
        print(f"Sum of 'Number of PRs' from 'cpython_fusil_report - cpython_fusil_report.csv.csv': {total_prs_main_csv}")
    else:
        print("'Number of PRs' column in 'cpython_fusil_report - cpython_fusil_report.csv.csv' is present but contains no numeric data.")
else:
    print("'Number of PRs' column not found or empty/all-NaN in 'cpython_fusil_report - cpython_fusil_report.csv.csv'.")

# Check 'Number of PRs' in df_summary if it was loaded
if df_summary is not None and 'Number of PRs' in df_summary.columns:
    print("Found 'Number of PRs' in 'cpython_fusil_report - Summary Table.csv'.")
    df_summary['Number of PRs num'] = pd.to_numeric(df_summary['Number of PRs'], errors='coerce')
    if df_summary['Number of PRs num'].notna().any():
         total_prs_summary_csv = df_summary['Number of PRs num'].sum()
         print(f"Sum of 'Number of PRs' from 'cpython_fusil_report - Summary Table.csv': {total_prs_summary_csv}")
         print("Detailed PR status (open/closed) is not available in this summary and would require parsing PR details from another source.")
    else:
        print("'Number of PRs' column in 'cpython_fusil_report - Summary Table.csv' is present but contains no numeric data or all NaNs after conversion.")
elif df_summary is None: 
    pass 
else: 
    print("'Number of PRs' column not found in the loaded 'cpython_fusil_report - Summary Table.csv'.")


print("For detailed PR counts (total, open, closed) and PR authors, we will likely need to refer to the information in the main Markdown table in `cpython_report.md` or specific PR analysis from another source/script.")


# --- Days Open Calculation (for closed issues) ---
df_closed_issues_for_days_calc = df_issues[
    (df_issues['Status'].str.lower() == 'closed') &
    (df_issues['Date Filed'].notna()) &
    (df_issues['Closed Date'].notna())
].copy()

if not df_closed_issues_for_days_calc.empty:
    df_closed_issues_for_days_calc['Days Open Calc'] = (df_closed_issues_for_days_calc['Closed Date'] - df_closed_issues_for_days_calc['Date Filed']).dt.days
    print("\n--- Days to Close (for closed issues from 'cpython_fusil_report - cpython_fusil_report.csv.csv') ---")
    
    if 'Days Open Calc' in df_closed_issues_for_days_calc.columns and df_closed_issues_for_days_calc['Days Open Calc'].notna().any():
        print(df_closed_issues_for_days_calc[['Issue #', 'Title', 'Days Open Calc']].head())
        
        valid_days_open = df_closed_issues_for_days_calc['Days Open Calc'].dropna()
        if not valid_days_open.empty:
            print(f"\nAverage days to close: {valid_days_open.mean():.2f} days")
            print(f"Median days to close: {valid_days_open.median()} days")

            df_closed_issues_for_days_calc[['Issue #', 'Days Open Calc']].to_csv("calculated_days_open_from_main_csv.csv", index=False)
            print("\nSaved 'Issue #' and calculated 'Days Open Calc' to 'calculated_days_open_from_main_csv.csv'")
        else:
            print("\nAll 'Days Open Calc' values are invalid (NaN), so no statistics or CSV saved.")
    else:
        print("\n'Days Open Calc' column could not be populated with valid data (e.g., all NaNs due to date issues), so no statistics or CSV saved.")
else:
    print("\nCould not calculate 'Days Open': No issues found that are 'closed' and have valid 'Date Filed' and 'Closed Date' in 'cpython_fusil_report - cpython_fusil_report.csv.csv'.")

print("\nReminder: The separate file 'cpython_fusil_report - Days to close an issue.csv' might also contain pre-calculated 'days to close' information.")
print("It would be good to compare if this calculation matches that file.")
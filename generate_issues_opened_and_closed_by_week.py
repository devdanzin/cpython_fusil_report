import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
file_path = "cpython_fusil_report - Issues created and closed per week.csv"
df_weekly_raw = None # Initialize

try:
    df_weekly_raw = pd.read_csv(file_path)
    print(f"Successfully loaded '{file_path}'. First 5 rows:")
    print(df_weekly_raw.head())
    print("\nRaw data info:")
    df_weekly_raw.info()

    # User specified data is in columns 3, 4, and 5 (1-indexed).
    # In 0-indexed pandas, these are columns 2, 3, and 4.
    if df_weekly_raw.shape[1] > 4: # Check if there are enough columns (0, 1, 2, 3, 4)
        df_cleaned = df_weekly_raw.iloc[:, [2, 3, 4]].copy()
        df_cleaned.columns = ['Week', 'Issues_Created', 'Issues_Closed']
    else:
        raise IndexError(f"The CSV file '{file_path}' has fewer than 5 columns. Cannot select columns 3, 4, and 5 (0-indexed 2, 3, 4). Please check file structure.")

    # Convert data to numeric, coercing errors for robustness
    df_cleaned['Week'] = pd.to_numeric(df_cleaned['Week'], errors='coerce')
    df_cleaned['Issues_Created'] = pd.to_numeric(df_cleaned['Issues_Created'], errors='coerce')
    df_cleaned['Issues_Closed'] = pd.to_numeric(df_cleaned['Issues_Closed'], errors='coerce')

    # Drop rows where essential data is NaN after coercion
    df_cleaned.dropna(subset=['Week', 'Issues_Created', 'Issues_Closed'], inplace=True)
    
    if not df_cleaned.empty:
        df_cleaned['Issues_Created'] = df_cleaned['Issues_Created'].astype(int)
        df_cleaned['Issues_Closed'] = df_cleaned['Issues_Closed'].astype(int)
        df_cleaned['Week'] = df_cleaned['Week'].astype(int)
    else:
        print("Warning: Cleaned DataFrame is empty. Check CSV content and column selection.")

    # Save the cleaned data
    cleaned_csv_path = "cleaned_issues_per_week.csv"
    df_cleaned.to_csv(cleaned_csv_path, index=False)
    print(f"\nCleaned data saved to '{cleaned_csv_path}'")
    if not df_cleaned.empty:
        print("Cleaned data head:")
        print(df_cleaned.head())
    else:
        print("Cleaned data is empty, so no head to display.")


    if not df_cleaned.empty:
        plt.style.use('seaborn-v0_8-whitegrid') 
        fig, ax = plt.subplots(figsize=(14, 7))

        bar_width = 0.35
        index = np.arange(len(df_cleaned['Week']))

        ax.bar(index - bar_width/2, df_cleaned['Issues_Created'], bar_width,
                              label='Issues Created', color='royalblue') 
        ax.bar(index + bar_width/2, df_cleaned['Issues_Closed'], bar_width,
                             label='Issues Closed', color='salmon')  

        ax.set_title('Issues Created and Closed per Week', fontsize=16)
        ax.set_xlabel('Week Number (Year)', fontsize=12) 
        ax.set_ylabel('Number of Issues', fontsize=12)

        tick_labels = []
        current_year_label = "'24" 
        last_week_num = 0 
        for week_num in df_cleaned['Week']:
            if week_num < last_week_num and last_week_num > 40 : 
                current_year_label = "'25"
            tick_labels.append(f"W{week_num:02d}\n{current_year_label}")
            last_week_num = week_num
        
        ax.set_xticks(index)
        ax.set_xticklabels(tick_labels, rotation=45, ha="right")

        max_issues_on_plot = 0
        if not df_cleaned['Issues_Created'].empty: # Check if Series is empty
            max_issues_on_plot = max(max_issues_on_plot, df_cleaned['Issues_Created'].max(skipna=True)) # Added skipna
        if not df_cleaned['Issues_Closed'].empty: # Check if Series is empty
            max_issues_on_plot = max(max_issues_on_plot, df_cleaned['Issues_Closed'].max(skipna=True)) # Added skipna
        
        y_upper_limit = max(10, int(max_issues_on_plot) if pd.notna(max_issues_on_plot) else 10) # Handle potential NaN from max() on empty
        ax.set_yticks(np.arange(0, y_upper_limit + 1, 1)) 
        ax.set_ylim(bottom=0, top=y_upper_limit + 0.5) 

        ax.legend()
        plt.tight_layout()
        
        plot_filename = "issues_created_closed_per_week_plot.png"
        plt.savefig(plot_filename)
        print(f"\nGraph saved as '{plot_filename}'")
    else:
        print("\nSkipping plot generation as the cleaned data is empty.")

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except IndexError as e:
    print(f"Error processing CSV columns: {e}")
    if df_weekly_raw is not None: 
        print("Displaying first 5 rows of the raw loaded CSV to help diagnose:")
        print(df_weekly_raw.head())
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if df_weekly_raw is not None:
        print("Displaying first 5 rows of the raw loaded CSV to help diagnose:")
        print(df_weekly_raw.head())
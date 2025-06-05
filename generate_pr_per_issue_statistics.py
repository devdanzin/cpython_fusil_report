import pandas as pd
from collections import Counter

try:
    # Load the Summary Table CSV
    df_summary = pd.read_csv("cpython_fusil_report - Summary Table.csv")
    print("Successfully loaded 'cpython_fusil_report - Summary Table.csv'")

    # --- Analyze 'PR authors' column ---
    all_pr_authors_per_issue = []
    
    if 'PR authors' in df_summary.columns:
        # Iterate through each entry in the 'PR authors' column
        for author_list_str in df_summary['PR authors'].dropna(): 
            if isinstance(author_list_str, str) and author_list_str.strip(): 
                authors = author_list_str.split(',')
                for author in authors:
                    normalized_author = author.strip().lstrip('@') 
                    if normalized_author: 
                        all_pr_authors_per_issue.append(normalized_author)
        
        if not all_pr_authors_per_issue:
            print("No PR authors found in the 'PR authors' column after processing, or the column is effectively empty.")
        else:
            author_issue_counts = Counter(all_pr_authors_per_issue)
            
            print("\n--- PR Author Involvement (Number of Issues per Author) ---")
            sorted_authors = author_issue_counts.most_common()
            
            for author, count in sorted_authors:
                print(f"{author}: {count} issues")
            
            total_unique_authors = len(sorted_authors)
            print(f"\nTotal unique PR authors: {total_unique_authors}")
            
            if sorted_authors:
                top_author_name, top_author_count = sorted_authors[0]
                print(f"\nThe developer involved in the most issues ({top_author_count}) was {top_author_name}.")
                if len(sorted_authors) > 1:
                    second_author_name, second_author_count = sorted_authors[1]
                    # Ensure there's actually a second author to prevent index error if only one author total
                    if second_author_name: 
                        print(f"The second most involved developer ({second_author_count}) was {second_author_name}.")
            else:
                print("\nNo author data to determine the top contributor.")

    else:
        print("Error: 'PR authors' column not found in 'cpython_fusil_report - Summary Table.csv'.")

except FileNotFoundError:
    print("Error: 'cpython_fusil_report - Summary Table.csv' not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

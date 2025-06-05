import re
from collections import Counter

def parse_appendix_for_pr_data(report_content):
    """
    Parses the Appendix section of the report to extract PR authors,
    their PR association counts, and the total number of unique PRs.

    Args:
        report_content (str): The full string content of the cpython_report.md file.

    Returns:
        tuple: (pr_author_counts, total_unique_prs_found, parsing_issues)
               pr_author_counts (Counter): Authors as keys, their PR association counts as values.
               total_unique_prs_found (int): Total number of unique PRs found.
               parsing_issues (list): Descriptions of parsing inconsistencies.
    """
    pr_author_association_counts = Counter()
    total_unique_prs_found = 0
    parsing_issues = []
    
    in_appendix_findings = False
    appendix_section_starts = ["## Appendix", "## Apendix"]
    findings_subsection_header = "### Findings"
    end_appendix_sections = ["## Conclusions", "## Impact"] 

    prs_header_pattern = re.compile(r"^\s*-\s*PRs\s*\(author\):", re.IGNORECASE)
    pr_line_pattern = re.compile(
        r"^\s*-\s*(?:\[\d+\]\(https?://[^\)]+\))?\s*\((@[^)]+)\)" 
    ) # Ensures authors are present
    
    lines = report_content.splitlines()
    
    for i, line in enumerate(lines):
        if not in_appendix_findings:
            if any(start_header in line for start_header in appendix_section_starts):
                if (i + 1 < len(lines) and findings_subsection_header in lines[i+1]) or \
                   (i + 2 < len(lines) and findings_subsection_header in lines[i+2]):
                    in_appendix_findings = True
                    print("INFO: Entered Appendix Findings section for PR parsing.")
            continue
        
        if any(end_header in line for end_header in end_appendix_sections) and line.startswith("## "):
            print(f"INFO: Reached section '{line}', stopping PR parse for Appendix.")
            break

        if prs_header_pattern.search(line):
            line_index = i + 1
            while line_index < len(lines) and lines[line_index].strip().startswith("- "):
                pr_line_text = lines[line_index].strip()
                
                if "None yet" in pr_line_text or "None" in pr_line_text.strip():
                    line_index += 1
                    continue

                match_pr = pr_line_pattern.search(pr_line_text)
                
                if match_pr:
                    # This line is considered one unique PR
                    total_unique_prs_found += 1 
                    
                    authors_group_str = match_pr.group(1) 
                    authors_in_pr = [
                        author.strip().lstrip('@') 
                        for author in authors_group_str.split(',') 
                        if author.strip()
                    ]
                    
                    if not authors_in_pr:
                        log_msg = f"WARNING: Parsed empty author list from group '({authors_group_str})' in PR line: '{pr_line_text}' (Line ~{line_index+1})"
                        parsing_issues.append(log_msg)
                    else:
                        for author_name in authors_in_pr:
                            if author_name:
                                pr_author_association_counts[author_name] += 1
                else:
                    log_msg = f"WARNING: Line under 'PRs (author):' did not match expected PR-author pattern (and not 'None yet'): '{pr_line_text}' (Line ~{line_index+1})"
                    parsing_issues.append(log_msg)
                
                line_index += 1
            i = line_index - 1 
            
    return pr_author_association_counts, total_unique_prs_found, parsing_issues

# --- Main execution part ---
if __name__ == "__main__":
    report_file_path = "cpython_report.md" 
    
    try:
        with open(report_file_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        print(f"Successfully read '{report_file_path}'. Analyzing Appendix for PR data...")
        author_counts, total_prs, issues = parse_appendix_for_pr_data(report_content)
        
        print(f"\n--- Total Unique PRs Found in Appendix ---")
        print(f"Total distinct PRs listed: {total_prs}")

        if author_counts:
            print("\n--- Number of PRs Each Author is Associated With (from Appendix) ---")
            sorted_pr_authors = sorted(author_counts.items(), key=lambda item: (-item[1], item[0]))
            
            for author, count in sorted_pr_authors:
                print(f"{author}: {count} PRs associated") # Clarified meaning
            
            total_unique_authors = len(sorted_pr_authors)
            print(f"\nTotal unique PR authors found in Appendix: {total_unique_authors}")

            if sorted_pr_authors:
                top_author_name, top_author_pr_associations = sorted_pr_authors[0]
                print(f"\nThe author associated with the most PRs ({top_author_pr_associations}) was {top_author_name}.")
                if len(sorted_pr_authors) > 1:
                    second_author_name, second_author_pr_associations = sorted_pr_authors[1]
                    if second_author_name:
                         print(f"The second author associated with most PRs ({second_author_pr_associations}) was {second_author_name}.")
        else:
            print("\nNo PR author association data extracted from the Appendix.")
            
        if issues:
            print("\n--- Parsing Issues/Inconsistencies Found During Appendix Scan ---")
            for issue_desc in issues:
                print(issue_desc)
        else:
            print("\nNo major parsing inconsistencies detected in PR listings within Appendix.")
            
    except FileNotFoundError:
        print(f"Error: The report file '{report_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

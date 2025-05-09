import os
import csv
from github import Github
from github.GithubException import GithubException
from datetime import datetime

# --- Configuration ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = "python/cpython"
AUTHOR = "devdanzin"
SEARCH_KEYWORD = "fusil"  # Keyword to find in issues
OUTPUT_CSV_FILE = f"cpython_fusil_issues_by_{AUTHOR}.csv"


# --- Helper function for basic categorization (manual review is CRITICAL) ---
def guess_kind_from_labels_title(labels, title):
    title_lower = title.lower()
    label_set = {label.lower() for label in labels}
    if any(k in title_lower for k in ["segfault", "segmentation fault", "crash"]) or \
            any(k in label_set for k in ["crash", "segfault"]):
        return "Segfault/Crash"
    if "assertionerror" in title_lower or "abort" in title_lower or "assert" in title_lower or \
            any(k in label_set for k in ["assertionerror", "abort"]):
        return "Abort/AssertionError"
    if "systemerror" in title_lower or "system error" in title_lower or \
            "systemerror" in label_set:
        return "SystemError"
    if "fatal python error" in title_lower or "fatal error" in title_lower or \
            any(k in label_set for k in ["fatal-error"]):
        return "Fatal Python Error"
    return ""


def guess_versions_from_labels(labels):
    versions = set()
    for label in labels:
        label_lower = label.lower()
        if label_lower.startswith("version-") or label_lower.startswith("python-"):  # e.g., version-3.12
            ver = label_lower.replace("version-", "").replace("python-", "")
            versions.add(ver)
        elif "3." in label_lower:  # crude catch for "3.12", "3.13" etc. if not formally labeled
            parts = label_lower.split(".")
            if len(parts) > 1 and parts[0] == "3" and parts[1].isdigit():
                versions.add(f"{parts[0]}.{parts[1]}")
    return ";".join(sorted(list(versions))) if versions else ""


def guess_configurations_from_labels(labels):
    configs = set()
    label_set = {label.lower() for label in labels}
    if "free-threading" in label_set or "freethreading" in label_set:
        configs.add("Free-threaded")
    if "debug-build" in label_set or "debug" in label_set:  # "debug" might be too broad
        configs.add("Debug Build")
    if "asan" in label_set or "addresssanitizer" in label_set:
        configs.add("ASAN")
    if "jit" in label_set:
        configs.add("JIT")
    # Add more common configurations you expect
    return ";".join(sorted(list(configs))) if configs else ""


def fetch_github_issues():
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set.")
        return

    g = Github(GITHUB_TOKEN)

    try:
        # Check user and rate limit
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
        print(f"Rate limit: {g.get_rate_limit()}")
    except GithubException as e:
        print(f"Error connecting to GitHub or authenticating: {e}")
        return

    query = f"repo:{REPO_NAME} author:{AUTHOR} is:issue sort:created-asc {SEARCH_KEYWORD}"
    print(f"Searching for issues with query: {query}\n")

    issues_data = []
    try:
        found_issues = g.search_issues(query=query)
        print(f"Found {found_issues.totalCount} issues matching the query.")

        for issue in found_issues:
            print(f"Processing Issue #{issue.number}: {issue.title}")

            labels = [label.name for label in issue.labels]
            assignees = [assignee.login for assignee in issue.assignees]
            milestone = issue.milestone.title if issue.milestone else ""

            body_snippet_lines = issue.body.splitlines()[:15]  # First 15 lines as snippet
            body_snippet = "\\n".join(body_snippet_lines)  # Escape newlines for CSV
            if len(issue.body) > len(body_snippet):
                body_snippet += "..."

            linked_prs_info = []
            # Attempt to find linked PRs through timeline events (cross-referenced)
            # This can be slow as it fetches timeline for each issue
            try:
                for event in issue.get_timeline():
                    if event.event == "cross-referenced" and \
                            hasattr(event, 'source') and event.source and \
                            hasattr(event.source, 'issue') and event.source.issue and \
                            hasattr(event.source.issue, 'pull_request') and event.source.issue.pull_request:

                        pr = event.source.issue  # This is the PR object
                        pr_author = pr.user.login if pr.user else "N/A"
                        pr_info = f"{pr.html_url};{pr_author};{pr.state}"
                        if pr_info not in linked_prs_info:  # Avoid duplicates
                            linked_prs_info.append(pr_info)
            except GithubException as e:
                print(f"  Warning: Could not fetch timeline for issue #{issue.number}: {e}")
            except Exception as e:
                print(f"  Warning: An unexpected error occurred while fetching timeline for issue #{issue.number}: {e}")

            issues_data.append({
                "Issue #": issue.number,
                "Title": issue.title,
                "HTML URL": issue.html_url,
                "Date Filed": issue.created_at.strftime("%Y-%m-%d") if issue.created_at else "",
                "Status": issue.state,
                "Closed Date": issue.closed_at.strftime("%Y-%m-%d") if issue.closed_at else "",
                "Labels": ";".join(labels),
                "Assignees": ";".join(assignees),
                "Milestone": milestone,
                "Body Snippet (MRE/Backtrace hint)": body_snippet,
                "Linked PRs (URL;Author;Status)": " | ".join(linked_prs_info),  # Use pipe to separate multiple PRs
                "Guessed Kind": guess_kind_from_labels_title(labels, issue.title),
                "Guessed CPython Versions": guess_versions_from_labels(labels),
                "Guessed Configurations": guess_configurations_from_labels(labels),
            })
            # Be mindful of rate limits if fetching timeline for many issues
            # print(f"Current rate limit: {g.get_rate_limit().core}")


    except GithubException as e:
        print(f"Error during GitHub search or processing: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    if not issues_data:
        print("No issues found or processed.")
        return

    # Write to CSV
    fieldnames = [
        "Issue #", "Title", "HTML URL", "Date Filed", "Status", "Closed Date",
        "Labels", "Assignees", "Milestone", "Body Snippet (MRE/Backtrace hint)",
        "Linked PRs (URL;Author;Status)",
        "Guessed Kind", "Guessed CPython Versions", "Guessed Configurations"
    ]

    try:
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data_row in issues_data:
                writer.writerow(data_row)
        print(f"\nSuccessfully wrote {len(issues_data)} issues to {OUTPUT_CSV_FILE}")
    except IOError:
        print(f"Error writing to CSV file {OUTPUT_CSV_FILE}")


if __name__ == "__main__":
    fetch_github_issues()

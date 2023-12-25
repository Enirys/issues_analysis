import os
import requests
from dotenv import load_dotenv
import csv

# Load environment variables from .env file
load_dotenv()

# Get GitHub token from environment variables
github_token = os.getenv("GITHUB_TOKEN")

# Check if the token is available
if github_token is None:
    raise ValueError("GitHub token is missing. Please set GITHUB_TOKEN in your .env file.")

# Set the GitHub repository
repository = "rails/rails"

# GitHub API endpoint for fetching issues
endpoint = f"https://api.github.com/repos/{repository}/issues"

# Parameters for the request
params = {
    "state": "all",  # Fetch both open and closed issues
    "per_page": 100,
    "page": 1,
}

# Headers for the request with the GitHub token
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json",
}

all_issues = []

def fetch_n_issues(number_of_issues):
    while number_of_issues > 0:
        # Update the per_page parameter if needed
        params["per_page"] = min(number_of_issues, 100)

        # Make the request to GitHub API
        response = requests.get(endpoint, params=params, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            issues = response.json()
            all_issues.extend(issues)
            number_of_issues -= len(issues)

            # Check if there are more pages
            if "next" in response.links and number_of_issues > 0:
                params["page"] += 1
            else:
                break
        else:
            raise RuntimeError(f"Failed to fetch issues. Status code: {response.status_code}, Error: {response.text}")

    return all_issues

def fetch_all_issues():
    while True:
        # Make the request to GitHub API
        response = requests.get(endpoint, params=params, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            issues = response.json()
            all_issues.extend(issues)

            # Check if there are more pages
            if "next" in response.links:
                params["page"] += 1
            else:
                break
        else:
            raise RuntimeError(f"Failed to fetch issues. Status code: {response.status_code}, Error: {response.text}")

    return all_issues

def save_to_csv(issues, csv_file_path):
    # Specify the fields to be included in the CSV
    fields = [
        'url', 'repository_url', 'labels_url', 'comments_url', 'events_url', 'html_url', 'id', 'node_id',
        'number', 'title', 'user', 'labels', 'state', 'locked', 'assignee', 'assignees', 'milestone',
        'comments', 'created_at', 'updated_at', 'closed_at', 'author_association', 'active_lock_reason',
        'pull_request', 'body', 'timeline_url', 'performed_via_github_app'
    ]

    # Open the CSV file for writing
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Create a CSV writer
        csvwriter = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')

        # Write the header
        csvwriter.writeheader()

        # Write the data
        csvwriter.writerows(issues)

def main():
    # Fetch a specified number of issues
    #number_of_issues_to_fetch = 10
    #issues = fetch_n_issues(number_of_issues_to_fetch)

    # Fetch all the issues in the Repository
    issues = fetch_all_issues(repository)

    # Set the CSV file path
    csv_file_path = "data/rails_github_issues_dataset_raw.csv"

    # Save issues to CSV
    save_to_csv(issues, csv_file_path)

if __name__ == "__main__":
    main()
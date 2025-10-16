# /scripts/update_issues.py (DIAGNOSTIC SCRIPT for Timeline Events)
import os
from github import Github, Auth

# --- 調査したい子イシューの番号を指定 ---
CHILD_ISSUE_NUMBER = 2

def main():
    try:
        print(f"--- Starting Timeline Diagnosis for Issue #{CHILD_ISSUE_NUMBER} ---")
        
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not repo_name or not github_token: 
            print("ERROR: Environment variables not set.")
            exit(1)

        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        
        print(f"Fetching issue #{CHILD_ISSUE_NUMBER}...")
        issue = repo.get_issue(CHILD_ISSUE_NUMBER)
        
        print(f"--- Found {issue.get_timeline().totalCount} timeline events. Listing all... ---")
        
        # タイムラインイベントを一つずつ調査
        for event in issue.get_timeline():
            print("\n----------------------------------------")
            # event.event でイベントの種類がわかる
            print(f"EVENT TYPE: {event.event}")
            # event.raw_data にAPIが返した生のデータがすべて含まれる
            print("RAW DATA:")
            print(event.raw_data)
            print("----------------------------------------")
            
        print("\n✨ Diagnosis complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()

# /scripts/update_issues.py (ULTIMATE DIAGNOSTIC SCRIPT)
import os
import json
from github import Github, Auth

# --- 調査したいIssueの番号をリストで指定 ---
ISSUE_NUMBERS_TO_INVESTIGATE = [1, 2]

def main():
    try:
        print("--- Starting Ultimate Diagnosis ---")
        
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not repo_name or not github_token: 
            print("ERROR: Environment variables not set.")
            exit(1)

        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        
        # 指定されたIssueを一つずつ調査
        for issue_number in ISSUE_NUMBERS_TO_INVESTIGATE:
            print(f"\n\n===========================================================")
            print(f"🕵️  DIAGNOSING ISSUE #{issue_number}")
            print(f"===========================================================")
            
            try:
                issue = repo.get_issue(issue_number)
                
                # 1. Issueオブジェクト自体の全生データを表示
                print("\n--- 🔬 Full Issue Object RAW DATA ---")
                # json.dumpsで見やすく整形して出力
                print(json.dumps(issue.raw_data, indent=2, ensure_ascii=False))
                
                # 2. Issueのタイムラインイベントをすべて表示
                print("\n--- 📜 Timeline Events ---")
                timeline_events = issue.get_timeline()
                print(f"Found {timeline_events.totalCount} timeline events for Issue #{issue_number}.")
                
                for i, event in enumerate(timeline_events):
                    print(f"\n--- Event {i+1} ---")
                    print(f"EVENT TYPE: {event.event}")
                    print("RAW DATA:")
                    print(json.dumps(event.raw_data, indent=2, ensure_ascii=False))

            except Exception as e:
                print(f"\nError processing Issue #{issue_number}: {e}")

        print("\n\n✨ Diagnosis complete.")

    except Exception as e:
        print(f"An error occurred during script execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()

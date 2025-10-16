# /scripts/update_issues.py (v2.1 Corrected and with Logs)
import os
from datetime import timezone, timedelta
from github import Github, Auth

# --- Settings ---
TEMPLATE_PATH = "scripts/template.html"
OUTPUT_PATH = "index.html"
ISSUE_LIMIT = 500 # 取得するIssueの上限

def get_jst_time(utc_time):
    """UTC時刻をJST（UTC+9）に変換してフォーマットする"""
    if utc_time is None:
        return ""
    jst = timezone(timedelta(hours=9))
    jst_time = utc_time.astimezone(jst)
    return jst_time.strftime('%Y-%m-%d %H:%M')

def generate_issue_html(issue, all_issues, parent_child_map, is_child=False):
    """指定されたIssueのHTMLを再帰的に生成する"""
    
    assignees_html = ""
    if issue.assignees:
        for assignee in issue.assignees:
            assignees_html += f'<img src="{assignee.avatar_url}" width="20" height="20" alt="{assignee.login}" title="{assignee.login}" style="border-radius: 50%; margin-right: 5px;">'

    labels_html = ""
    for label in issue.labels:
        hex_color = label.color
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        font_color = "#111" if yiq >= 128 else "white"
        labels_html += f'<span class="label" style="background-color: #{label.color}; color: {font_color};">{label.name}</span>'

    child_issues_html = ""
    if issue.number in parent_child_map:
        for child_id in parent_child_map[issue.number]:
            if child_id in all_issues:
                child_issue = all_issues[child_id]
                child_issues_html += generate_issue_html(child_issue, all_issues, parent_child_map, is_child=True)

    issue_class = "issue-child" if is_child else "issue-parent"
    
    if child_issues_html:
        html = f"""
        <div class="{issue_class}" id="issue-{issue.number}">
            <details>
                <summary>
                    <div class="issue-summary-line">
                        <span class="issue-title">#{issue.number} {issue.title}</span>
                        <div class="assignees">{assignees_html}</div>
                    </div>
                </summary>
                <div class="sub-issues-container">
                    {child_issues_html}
                </div>
            </details>
        </div>
        """
    else:
        html = f"""
        <div class="{issue_class}" id="issue-{issue.number}">
            <div class="issue-summary-line">
                <a href="{issue.html_url}" target="_blank" rel="noopener noreferrer" class="issue-title">#{issue.number} {issue.title}</a>
                <div class="assignees">{assignees_html}</div>
            </div>
        </div>
        """
    return html


def main():
    try:
        print("--- Starting Issue Page Generation ---")
        
        # --- 1. 全Issueのデータを取得 & マップ化 ---
        print("Step 1: Fetching all open issues...")
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not repo_name or not github_token: 
            print("ERROR: Environment variables not set.")
            exit(1)

        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        
        # --- 💡ここが修正箇所です💡 ---
        # per_page引数を削除し、結果をスライスして件数を制限する方式に変更
        issues_paginated_list = repo.get_issues(state='open')
        all_issues = {issue.number: issue for issue in issues_paginated_list[:ISSUE_LIMIT]}
        print(f"-> Found {len(all_issues)} open issues (limit: {ISSUE_LIMIT}).")

        # --- 2. 親子関係を解析 ---
        print("Step 2: Analyzing parent-child relationships...")
        parent_child_map = {}
        child_parent_map = {}

        for issue_number, issue in all_issues.items():
            for event in issue.get_timeline():
                if event.event == "cross-referenced" and hasattr(event, "source") and event.source.issue.repository.full_name == repo_name:
                    parent_issue_id = event.source.issue.number
                    child_issue_id = issue.number
                    if parent_issue_id in all_issues:
                        if parent_issue_id not in parent_child_map:
                            parent_child_map[parent_issue_id] = []
                        if child_issue_id not in parent_child_map[parent_issue_id]:
                            parent_child_map[parent_issue_id].append(child_issue_id)
                        child_parent_map[child_issue_id] = parent_issue_id
        
        print(f"-> Found {len(parent_child_map)} parent issues.")

        # --- 3. HTMLを生成 ---
        print("Step 3: Generating HTML content...")
        final_html = ""
        # トップレベルのIssue（自分が子でないIssue）だけを起点にHTML生成を開始
        sorted_issue_numbers = sorted(all_issues.keys())
        for issue_number in sorted_issue_numbers:
            if issue_number not in child_parent_map:
                final_html += generate_issue_html(all_issues[issue_number], all_issues, parent_child_map)
        
        if not final_html:
            final_html = "<p>No open issues.</p>"

        # --- 4. テンプレートに埋め込み、ファイル出力 ---
        print("Step 4: Writing to index.html...")
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        placeholder = "%%ISSUES_GO_HERE%%"
        new_content = content.replace(placeholder, final_html, 1)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✨ Successfully generated index.html!")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()

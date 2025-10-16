# /scripts/update_issues.py (FINAL VERSION with all features)
import os
from github import Github, Auth
from markdown_it import MarkdownIt

# --- Settings ---
TEMPLATE_PATH = "scripts/template.html"
OUTPUT_PATH = "index.html"
ISSUE_LIMIT = 500

md = MarkdownIt() # MarkdownをHTMLに変換するパーサーを初期化

def generate_issue_html(issue, all_issues, parent_child_map, is_child=False):
    """指定されたIssueのHTMLを再帰的に生成する"""
    
    assignees_html = ""
    if issue.assignees:
        for assignee in issue.assignees:
            assignees_html += f'<img src="{assignee.avatar_url}" width="20" height="20" alt="{assignee.login}" title="{assignee.login}" style="border-radius: 50%; margin-right: 5px;">'

    # 💡 Issue本文をHTMLに変換
    issue_body_html = md.render(issue.body) if issue.body else ""

    child_issues_html = ""
    if issue.number in parent_child_map:
        for child_id in parent_child_map[issue.number]:
            if child_id in all_issues:
                child_issue = all_issues[child_id]
                # 子Issueはサマリー（タイトル行）だけを再帰的に生成
                child_issues_html += generate_issue_html(child_issue, all_issues, parent_child_map, is_child=True)

    issue_class = "issue-child" if is_child else "issue-parent"
    
    # 子がいる場合は<details>タグでアコーディオンにする
    if not is_child and child_issues_html:
        html = f"""
        <div class="{issue_class}" id="issue-{issue.number}">
            <details>
                <summary>
                    <div class="issue-summary-line">
                        <span class="issue-title">#{issue.number} {issue.title}</span>
                        <div class="assignees">{assignees_html}</div>
                    </div>
                </summary>
                <div class="issue-body">{issue_body_html}</div>
                <div class="sub-issues-container">
                    <h4>Sub-issues</h4>
                    {child_issues_html}
                </div>
            </details>
        </div>
        """
    else: # 子がいないIssue、または自分自身が子Issueの場合
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
        print("--- Starting Final Issue Page Generation ---")
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not repo_name or not github_token: exit(1)

        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        
        issues_paginated_list = repo.get_issues(state='open')
        all_issues = {issue.number: issue for issue in issues_paginated_list[:ISSUE_LIMIT]}
        print(f"-> Found {len(all_issues)} open issues.")

        parent_child_map = {}
        child_parent_map = {}

        # 💡 親子判定ロジックをより正確なものに修正
        for issue in all_issues.values():
            for event in issue.get_timeline():
                if event.event == "cross-referenced" and event.source and event.source.issue and event.source.issue.repository.full_name == repo_name:
                    # 子Issueのタイムラインには「親にトラックされた」という相互参照イベントが記録される
                    parent_issue_id = event.source.issue.number
                    child_issue_id = issue.number
                    if parent_issue_id in all_issues:
                        if parent_issue_id not in parent_child_map:
                            parent_child_map[parent_issue_id] = []
                        if child_issue_id not in parent_child_map[parent_issue_id]:
                            parent_child_map[parent_issue_id].append(child_issue_id)
                        child_parent_map[child_issue_id] = parent_issue_id
        
        print(f"-> Found {len(parent_child_map)} parent issues.")

        final_html = ""
        sorted_issue_numbers = sorted(all_issues.keys())
        for issue_number in sorted_issue_numbers:
            if issue_number not in child_parent_map:
                final_html += generate_issue_html(all_issues[issue_number], all_issues, parent_child_map)
        
        if not final_html:
            final_html = "<p>No open issues.</p>"

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        placeholder = "%%ISSUES_GO_HERE%%"
        new_content = content.replace(placeholder, final_html, 1)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✨ Successfully generated index.html with all features!")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()

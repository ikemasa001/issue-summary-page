# /scripts/update_issues.py (Link Preview Debug Version)
import os
import re
import requests
from github import Github, Auth
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup

# --- Settings ---
TEMPLATE_PATH = "scripts/template.html"
OUTPUT_PATH = "index.html"
ISSUE_LIMIT = 500
md = MarkdownIt()

# --- リンクプレビュー用の関数 ---
def create_link_previews(markdown_text):
    """Markdownテキスト内のURLをプレビューカードに置き換える"""
    url_pattern = r'(?<!href=")(https://[^\s<]+)'
    
    def replace_url_with_preview(match):
        url = match.group(1)
        try:
            print(f"\n--- 🐞 DEBUG: Fetching URL: {url} ---")
            
            # 多くのサイトはボットを検知するため、人間のブラウザを装う
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(url, timeout=5, headers=headers)
            print(f"-> Status Code: {response.status_code}")

            # 💡 --- ここがデバッグコードです --- 💡
            # 取得したHTMLの*全体*をログに出力
            print("\n-> Received FULL HTML:")
            print(response.text)
            print("---------------------------------\n")
            # --- デバッグコードここまで ---

            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('meta', property='og:title')
            image = soup.find('meta', property='og:image')
            
            if not title or not image:
                print("-> 'og:title' or 'og:image' not found. Using regular link.")
                return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
            
            description = soup.find('meta', property='og:description')
            site_name = soup.find('meta', property='og:site_name')

            print("-> Success! 'og:image' and 'og:title' found. Generating preview card.")
            return f"""
            <a href="{url}" target="_blank" rel="noopener noreferrer" class="link-preview">
                <div class="preview-image"><img src="{image['content']}" alt="Preview Image"></div>
                <div class="preview-content">
                    <div class="preview-title">{title['content']}</div>
                    <div class="preview-description">{description['content'] if description else ''}</div>
                    <div class="preview-site">{site_name['content'] if site_name else url.split('/')[2]}</div>
                </div>
            </a>
            """
        except Exception as e:
            print(f"Could not generate preview for {url}: {e}")
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'

    return re.sub(url_pattern, replace_url_with_preview, markdown_text)


def generate_child_issue_summary_html(issue): # (変更なし)
    assignees_html = ""
    if issue.assignees:
        for assignee in issue.assignees:
            assignees_html += f'<img src="{assignee.avatar_url}" width="20" height="20" alt="{assignee.login}" title="{assignee.login}" style="border-radius: 50%;">'
    label_names = ",".join([label.name for label in issue.labels])
    return f"""
    <div class="issue-child" id="issue-{issue.number}" data-labels="{label_names}">
        <div class="issue-summary-line">
            <a href="{issue.html_url}" target="_blank" rel="noopener noreferrer" class="issue-title">#{issue.number} {issue.title}</a>
            <div class="assignees">{assignees_html}</div>
        </div>
    </div>
    """

def generate_issue_html(issue, all_issues, parent_child_map): # (変更なし)
    assignees_html = ""
    if issue.assignees:
        for assignee in issue.assignees:
            assignees_html += f'<img src="{assignee.avatar_url}" width="20" height="20" alt="{assignee.login}" title="{assignee.login}" style="border-radius: 50%;">'
    body_with_previews = create_link_previews(issue.body) if issue.body else ""
    issue_body_html = md.render(body_with_previews)
    label_names = ",".join([label.name for label in issue.labels])
    html = f"""
    <div class="issue-parent" id="issue-{issue.number}" data-labels="{label_names}">
        <div class="issue-main-content">
            <div class="issue-summary-line">
                <span class="issue-title">#{issue.number} {issue.title}</span>
                <div class="meta-container">
                    <div class="assignees">{assignees_html}</div>
                    <div class="actions-container">
                        <button class="action-button share-button" data-title="#{issue.number} {issue.title}" data-id="{issue.number}">共有</button>
                        <button class="action-button copy-button" data-id="{issue.number}">リンクをコピー</button>
                    </div>
                </div>
            </div>
            <div class="issue-body">{issue_body_html}</div>
        </div>
    """
    if issue.number in parent_child_map:
        child_issues_html = ""
        child_count = len(parent_child_map[issue.number])
        for child_id in parent_child_map[issue.number]:
            if child_id in all_issues:
                child_issues_html += generate_child_issue_summary_html(all_issues[child_id])
        html += f"""
        <div class="sub-issues-section">
            <details>
                <summary>Sub-issues ({child_count})</summary>
                <div class="sub-issues-container">{child_issues_html}</div>
            </details>
        </div>
        """
    html += "</div>"
    return html

def main(): # (main関数は変更なし)
    try:
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")
        if not repo_name or not github_token: exit(1)
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        issues_paginated_list = repo.get_issues(state='open')
        all_issues = {issue.number: issue for issue in issues_paginated_list[:ISSUE_LIMIT]}
        parent_child_map = {}
        child_parent_map = {}
        for issue in all_issues.values():
            if 'parent_issue_url' in issue.raw_data and issue.raw_data['parent_issue_url']:
                parent_issue_number = int(issue.raw_data['parent_issue_url'].split('/')[-1])
                child_issue_number = issue.number
                if parent_issue_number in all_issues:
                    if parent_issue_number not in parent_child_map: parent_child_map[parent_issue_number] = []
                    parent_child_map[parent_issue_number].append(child_issue_number)
                    child_parent_map[child_issue_number] = parent_issue_number
        final_html = ""
        sorted_issue_numbers = sorted(all_issues.keys())
        for issue_number in sorted_issue_numbers:
            if issue_number not in child_parent_map:
                final_html += generate_issue_html(all_issues[issue_number], all_issues, parent_child_map)
        if not final_html: final_html = "<p>No open issues.</p>"
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

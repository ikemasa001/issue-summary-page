# /scripts/update_issues.py (FINAL VERSION v2)
import os
from github import Github, Auth

TEMPLATE_PATH = "scripts/template.html"
OUTPUT_PATH = "index.html"
ISSUE_LIMIT = 200

def main():
    try:
        repo_name = os.environ.get("REPO_NAME")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not repo_name or not github_token:
            print("ERROR: Required environment variables are not set.")
            exit(1)

        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state='open')

        issues_html = ""
        issue_count = 0
        
        for issue in issues:
            if issue_count >= ISSUE_LIMIT:
                break
            if issue.pull_request:
                continue

            labels_html = ""
            for label in issue.labels:
                hex_color = label.color
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
                font_color = "#111" if yiq >= 128 else "white"
                labels_html += f'<span class="label" style="background-color: #{label.color}; color: {font_color};">{label.name}</span>'
            
            issues_html += f"""
            <div class="issue">
                <h2><a href="{issue.html_url}" target="_blank" rel="noopener noreferrer">#{issue.number} {issue.title}</a></h2>
                <div class="issue-meta">
                    <span>by {issue.user.login}</span>
                </div>
                <div>{labels_html}</div>
            </div>
            """
            issue_count += 1

        if not issues_html:
            issues_html = "<p>No open issues.</p>"
        
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # 新しい、安全なプレースホルダーを使用
        placeholder = "%%ISSUES_GO_HERE%%"
        
        parts = content.split(placeholder)

        if len(parts) == 2:
            new_content = parts[0] + issues_html + parts[1]
        else:
            print(f"WARNING: Placeholder '{placeholder}' not found or found multiple times.")
            new_content = content 

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"Successfully generated {OUTPUT_PATH} ({issue_count} issue(s))")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()

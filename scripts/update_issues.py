# /scripts/update_issues.py
import os
from github import Github

# --- 設定 ---
# テンプレートファイルのパス
TEMPLATE_PATH = "scripts/template.html"
# 出力ファイルのパス
OUTPUT_PATH = "index.html"
# 取得するIssueの上限数（安全装置）
ISSUE_LIMIT = 200

def main():
    """
    GitHubリポジトリのIssueを取得し、テンプレートからindex.htmlを生成する
    """
    repo_name = os.environ.get("REPO_NAME")
    github_token = os.environ.get("GITHUB_TOKEN")

    if not repo_name or not github_token:
        print("エラー: 必要な環境変数が設定されていません。")
        exit(1)

    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state='open')

        issues_html = ""
        issue_count = 0
        # 上限数に達するか、Issueがなくなるまでループ
        for issue in issues:
            if issue_count >= ISSUE_LIMIT:
                print(f"警告: Issueが多いため、上限の{ISSUE_LIMIT}件で中断しました。")
                break

            # PRは除外する
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
            issues_html = "<p>現在オープンなIssueはありません。</p>"

        # テンプレートファイルを読み込む
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # の部分を生成したHTMLで置換
        new_content = content.replace("", issues_html)

        # 新しいindex.htmlとして書き出す（常に上書き）
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"{OUTPUT_PATH} の生成が完了しました。({issue_count}件のIssue)")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        exit(1)

if __name__ == "__main__":
    main()

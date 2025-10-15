# /scripts/update_issues.py
import os
from github import Github

def main():
    """
    GitHubリポジトリのIssueを取得し、index.htmlを更新するメイン関数
    """
    # --- 環境変数から情報を取得 ---
    # GitHub Actionsが自動的に設定する環境変数
    repo_name = os.environ.get("REPO_NAME")
    # Step6で設定したSecret
    github_token = os.environ.get("GITHUB_TOKEN")

    if not repo_name or not github_token:
        print("エラー: 必要な環境変数（REPO_NAME, GITHUB_TOKEN）が設定されていません。")
        return

    try:
        # --- GitHub APIに接続 ---
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        # オープンなIssueをすべて取得
        issues = repo.get_issues(state='open')

        # --- HTMLコンテンツを生成 ---
        issues_html = ""
        if issues.totalCount > 0:
            for issue in issues:
                # ラベルのHTMLを生成
                labels_html = ""
                for label in issue.labels:
                    # ラベルの色を16進数で取得し、コントラストを考慮して文字色を決定
                    hex_color = label.color
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    # YIQ式で輝度を計算
                    yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
                    font_color = "#111" if yiq >= 128 else "white"

                    labels_html += f'<span class="label" style="background-color: #{label.color}; color: {font_color};">{label.name}</span>'

                # IssueごとのHTMLを生成
                issues_html += f"""
                <div class="issue">
                    <h2><a href="{issue.html_url}" target="_blank" rel="noopener noreferrer">#{issue.number} {issue.title}</a></h2>
                    <div class="issue-meta">
                        <span>by {issue.user.login}</span>
                    </div>
                    <div>{labels_html}</div>
                </div>
                """
        else:
            issues_html = "<p>現在オープンなIssueはありません。</p>"

        # --- index.htmlを読み込んで置換 ---
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()

        # の部分を生成したHTMLで置換
        new_content = content.replace("", issues_html)

        # --- 更新した内容をindex.htmlに書き込み ---
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("index.htmlの更新が完了しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()

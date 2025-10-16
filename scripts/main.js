// /main.js

// ページのHTMLがすべて読み込まれてからスクリプトを実行する
document.addEventListener('DOMContentLoaded', () => {
    const issuesContainer = document.getElementById('issues');
    const filtersContainer = document.getElementById('filters');
    
    // 表示されているすべてのIssue要素を取得
    const allIssues = issuesContainer.querySelectorAll('.issue-parent, .issue-child');
    if (allIssues.length === 0) return;

    // --- 1. Issueからラベルを収集し、フィルターボタンを自動生成 ---
    const allLabels = new Set();
    allIssues.forEach(issue => {
        const labels = issue.dataset.labels;
        if (labels) {
            labels.split(',').forEach(label => allLabels.add(label));
        }
    });

    // 「すべて」ボタンを最初に作成
    let buttonsHTML = '<button class="filter-button active" data-label="all">すべて</button>';
    
    // 各ラベルのボタンを作成
    Array.from(allLabels).sort().forEach(label => {
        buttonsHTML += `<button class="filter-button" data-label="${label}">${label}</button>`;
    });

    filtersContainer.innerHTML = buttonsHTML;

    // --- 2. フィルタリングのロジックを定義 ---
    const filterButtons = filtersContainer.querySelectorAll('.filter-button');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedLabel = button.dataset.label;

            // ボタンの選択状態を更新
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Issueの表示・非表示を切り替え
            allIssues.forEach(issue => {
                if (selectedLabel === 'all') {
                    issue.style.display = ''; // 表示
                } else {
                    const issueLabels = issue.dataset.labels.split(',');
                    if (issueLabels.includes(selectedLabel)) {
                        issue.style.display = ''; // 表示
                    } else {
                        issue.style.display = 'none'; // 非表示
                    }
                }
            });
        });
    });
});

// /main.js
document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. フィルター機能 ---
    const issuesContainer = document.getElementById('issues');
    const filtersContainer = document.getElementById('filters');
    
    // issuesContainerとfiltersContainerが存在する場合のみ実行
    if (issuesContainer && filtersContainer) {
        const allIssues = issuesContainer.querySelectorAll('.issue-parent, .issue-child');
        
        if (allIssues.length > 0) {
            const allLabels = new Set();
            // ページ内の全Issueからラベルを収集
            allIssues.forEach(issue => {
                const labels = issue.dataset.labels;
                if (labels) {
                    labels.split(',').forEach(label => { 
                        if (label) allLabels.add(label); // 空のラベルを除外
                    });
                }
            });

            // ラベルが1つ以上存在する場合のみボタンを生成
            if (allLabels.size > 0) {
                let buttonsHTML = '<button class="filter-button active" data-label="all">すべて</button>';
                Array.from(allLabels).sort().forEach(label => {
                    buttonsHTML += `<button class="filter-button" data-label="${label}">${label}</button>`;
                });
                filtersContainer.innerHTML = buttonsHTML;

                // ボタンにクリックイベントを割り当て
                const filterButtons = filtersContainer.querySelectorAll('.filter-button');
                filterButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        const selectedLabel = button.dataset.label;

                        // ボタンのアクティブ状態を更新
                        filterButtons.forEach(btn => btn.classList.remove('active'));
                        button.classList.add('active');

                        // Issueの表示・非表示を切り替え
                        allIssues.forEach(issue => {
                            if (selectedLabel === 'all') {
                                issue.style.display = ''; // 表示
                            } else {
                                const issueLabels = issue.dataset.labels ? issue.dataset.labels.split(',') : [];
                                if (issueLabels.includes(selectedLabel)) {
                                    issue.style.display = ''; // 表示
                                } else {
                                    issue.style.display = 'none'; // 非表示
                                }
                            }
                        });
                    });
                });
            }
        }
    }

    // --- 2. 共有機能 ---
    
    // Web Share APIが使えないブラウザでは「共有」ボタンをすべて非表示にする
    if (!navigator.share) {
        document.querySelectorAll('.share-button').forEach(button => {
            button.style.display = 'none';
        });
    }

    // 「共有」ボタンの処理
    document.querySelectorAll('.share-button').forEach(button => {
        button.addEventListener('click', async (event) => {
            event.stopPropagation(); // 親要素へのイベント伝播を停止
            const title = button.dataset.title;
            const url = `${window.location.origin}${window.location.pathname}#issue-${button.dataset.id}`;
            try {
                await navigator.share({
                    title: title,
                    text: `GitHub Issue: ${title}`,
                    url: url,
                });
            } catch (err) {
                console.error('Share failed:', err);
            }
        });
    });

    // 「リンクをコピー」ボタンの処理
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', (event) => {
            event.stopPropagation(); // 親要素へのイベント伝播を停止
            const url = `${window.location.origin}${window.location.pathname}#issue-${button.dataset.id}`;
            navigator.clipboard.writeText(url).then(() => {
                const originalText = button.textContent;
                button.textContent = 'コピーしました!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000); // 2秒後に元に戻す
            }).catch(err => {
                console.error('Copy failed:', err);
            });
        });
    });
    
});

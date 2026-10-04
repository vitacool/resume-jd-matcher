const historyList = document.querySelector("#history-list");
const detail = document.querySelector("#detail");
const refreshButton = document.querySelector("#refresh");

function tagList(items, missing = false) {
  if (!items.length) {
    return '<span class="empty">暂无</span>';
  }
  return items
    .map((item) => `<span class="tag ${missing ? "missing" : ""}">${item}</span>`)
    .join("");
}

function list(items) {
  return `<ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

async function loadHistory() {
  historyList.innerHTML = '<p class="empty">加载中...</p>';
  const response = await fetch("/api/history?limit=30");
  const data = await response.json();

  if (!data.items.length) {
    historyList.innerHTML = '<p class="empty">暂无分析记录。</p>';
    return;
  }

  historyList.innerHTML = data.items
    .map(
      (item) => `
        <article class="history-item">
          <header>
            <strong>${item.score} 分 · ${item.level}</strong>
            <span>${item.created_at}</span>
          </header>
          <p>${item.jd_preview}...</p>
          <div class="history-actions">
            <button type="button" data-view="${item.id}">查看</button>
            <button type="button" class="danger" data-delete="${item.id}">删除</button>
          </div>
        </article>
      `,
    )
    .join("");
}

async function showDetail(id) {
  const response = await fetch(`/api/history/${id}`);
  const data = await response.json();
  const result = data.result;

  detail.innerHTML = `
    <div class="score-row">
      <div class="score-card"><span>${result.score}</span><small>匹配分</small></div>
      <div>
        <p class="level">${result.level}</p>
        <p class="route">${result.route.target_role}：${result.route.focus}</p>
      </div>
    </div>

    <div class="detail-block">
      <h3>匹配关键词</h3>
      <div class="tags">${tagList(result.matched_keywords)}</div>
    </div>
    <div class="detail-block">
      <h3>缺失关键词</h3>
      <div class="tags">${tagList(result.missing_keywords, true)}</div>
    </div>
    <div class="detail-block">
      <h3>修改建议</h3>
      ${list(result.suggestions)}
    </div>
    <div class="detail-block">
      <h3>岗位 JD</h3>
      <pre>${data.jd_text}</pre>
    </div>
  `;
}

async function deleteItem(id) {
  await fetch(`/api/history/${id}`, { method: "DELETE" });
  detail.innerHTML = '<div class="detail-empty">选择一条记录查看完整分析。</div>';
  await loadHistory();
}

historyList.addEventListener("click", async (event) => {
  const viewId = event.target.dataset.view;
  const deleteId = event.target.dataset.delete;
  if (viewId) {
    await showDetail(viewId);
  }
  if (deleteId) {
    await deleteItem(deleteId);
  }
});

refreshButton.addEventListener("click", loadHistory);
loadHistory();

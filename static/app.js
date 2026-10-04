const resumeInput = document.querySelector("#resume");
const jdInput = document.querySelector("#jd");
const analyzeButton = document.querySelector("#analyze");
const fillDemoButton = document.querySelector("#fill-demo");
const statusText = document.querySelector("#status");

const demoResume = `林锦浩，软件工程本科，熟悉 Python、FastAPI、SQLite、HTML/CSS/JavaScript。
项目一：校园智能问答 Agent，使用 FastAPI 构建后端接口，支持 RAG 知识库检索、Embedding 向量检索、Agent 工具路由、后台知识库管理和用户反馈记录。
项目二：校园通知文本分类系统，使用 PyTorch 训练字符级文本分类模型，提供 /api/predict 和 /api/route 接口，支持 SQLite 预测日志、人工纠错、模型评估和后台管理页面。`;

const demoJd = `AI 应用开发实习生。要求熟悉 Python，了解 FastAPI 或 Flask，具备基础数据结构和算法能力；了解大模型应用、RAG、Embedding、向量检索、Agent 工具调用更佳；有 PyTorch、文本分类、模型评估、数据库和前端页面开发经验优先。`;

function renderTags(element, items, missing = false) {
  if (!items.length) {
    element.className = "tags empty";
    element.textContent = "暂无";
    return;
  }
  element.className = "tags";
  element.innerHTML = items
    .map((item) => `<span class="tag ${missing ? "missing" : ""}">${item}</span>`)
    .join("");
}

function renderList(element, items) {
  element.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

function renderResult(data) {
  document.querySelector("#score").textContent = data.score;
  document.querySelector("#level").textContent = data.level;
  document.querySelector("#route").textContent = `${data.route.target_role}：${data.route.focus}`;
  renderTags(document.querySelector("#matched"), data.matched_keywords);
  renderTags(document.querySelector("#missing"), data.missing_keywords, true);
  renderList(document.querySelector("#strengths"), data.strengths);
  renderList(document.querySelector("#suggestions"), data.suggestions);
}

fillDemoButton.addEventListener("click", () => {
  resumeInput.value = demoResume;
  jdInput.value = demoJd;
});

analyzeButton.addEventListener("click", async () => {
  const resumeText = resumeInput.value.trim();
  const jdText = jdInput.value.trim();

  if (resumeText.length < 20 || jdText.length < 20) {
    statusText.textContent = "请输入完整内容";
    return;
  }

  analyzeButton.disabled = true;
  statusText.textContent = "分析中...";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, jd_text: jdText }),
    });

    if (!response.ok) {
      throw new Error("分析失败");
    }

    const data = await response.json();
    renderResult(data);
    statusText.textContent = `已保存记录 #${data.id}`;
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    analyzeButton.disabled = false;
  }
});

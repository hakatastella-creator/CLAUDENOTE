const apiKeyInput = document.getElementById("apiKey");
const saveBtn = document.getElementById("saveBtn");
const statusEl = document.getElementById("status");

chrome.storage.sync.get(["anthropicApiKey"], (data) => {
  if (data.anthropicApiKey) {
    apiKeyInput.value = data.anthropicApiKey;
  }
});

saveBtn.addEventListener("click", () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    setStatus("APIキーを入力してください", "error");
    return;
  }
  if (!key.startsWith("sk-ant-")) {
    setStatus("APIキーは 'sk-ant-' で始まる必要があります", "error");
    return;
  }
  chrome.storage.sync.set({ anthropicApiKey: key }, () => {
    setStatus("保存しました ✓", "ok");
  });
});

function setStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = "status " + (type || "");
}

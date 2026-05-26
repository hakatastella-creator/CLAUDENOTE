const STORAGE_SAMPLES_KEY = "stellaStyleSamples";

const apiKeyInput = document.getElementById("apiKey");
const saveBtn = document.getElementById("saveBtn");
const statusEl = document.getElementById("status");
const sampleCountEl = document.getElementById("sampleCount");
const clearSamplesBtn = document.getElementById("clearSamplesBtn");

chrome.storage.sync.get(["anthropicApiKey"], (data) => {
  if (data.anthropicApiKey) apiKeyInput.value = data.anthropicApiKey;
});

function refreshSampleCount() {
  chrome.storage.local.get([STORAGE_SAMPLES_KEY], (data) => {
    const samples = data[STORAGE_SAMPLES_KEY] || [];
    sampleCountEl.textContent = samples.length;
  });
}
refreshSampleCount();

saveBtn.addEventListener("click", () => {
  const key = apiKeyInput.value.trim();
  if (!key) return setStatus("APIキーを入力してください", "error");
  if (!key.startsWith("sk-ant-")) {
    return setStatus("APIキーは 'sk-ant-' で始まる必要があります", "error");
  }
  chrome.storage.sync.set({ anthropicApiKey: key }, () => {
    setStatus("保存しました ✓", "ok");
  });
});

clearSamplesBtn.addEventListener("click", () => {
  if (!confirm("学習サンプルを全て削除しますか？")) return;
  chrome.storage.local.set({ [STORAGE_SAMPLES_KEY]: [] }, () => {
    refreshSampleCount();
    setStatus("学習サンプルを削除しました", "ok");
  });
});

function setStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = "status " + (type || "");
}

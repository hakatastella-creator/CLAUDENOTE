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

// ============================================================
// 料金表画像の登録（content.js の PRICE_PLANS と順序・キーを一致させる）
// ============================================================
const PRICE_PLANS = [
  { key: "priceImage_1", label: "① インビザラインフル（抜歯あり）" },
  { key: "priceImage_2", label: "② インビザラインフル" },
  { key: "priceImage_3", label: "③ インビザライン モデレート" },
  { key: "priceImage_4", label: "④ インビザライン エクスプレス" },
  { key: "priceImage_5", label: "⑤ インビザライン ライト" },
];

const MAX_BYTES = 4 * 1024 * 1024; // 元ファイル 4MB まで

const priceList = document.getElementById("priceList");

PRICE_PLANS.forEach((plan) => {
  const row = document.createElement("div");

  const line = document.createElement("div");
  line.className = "price-row";

  const name = document.createElement("span");
  name.className = "plan-name";
  name.textContent = plan.label;

  const state = document.createElement("span");
  state.className = "plan-state";
  state.textContent = "未登録";

  const pickBtn = document.createElement("button");
  pickBtn.className = "pick";
  pickBtn.textContent = "選択";

  const clearBtn = document.createElement("button");
  clearBtn.className = "clear";
  clearBtn.textContent = "削除";

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/png,image/jpeg,image/webp";
  fileInput.style.display = "none";

  const thumb = document.createElement("img");
  thumb.className = "price-thumb";

  line.append(name, state, pickBtn, clearBtn);
  row.append(line, fileInput, thumb);
  priceList.append(row);

  function renderSet(dataUrl) {
    state.textContent = "登録済み ✓";
    state.classList.add("set");
    thumb.src = dataUrl;
    thumb.classList.add("show");
  }
  function renderUnset() {
    state.textContent = "未登録";
    state.classList.remove("set");
    thumb.removeAttribute("src");
    thumb.classList.remove("show");
  }

  // 既存の登録を読み込み
  chrome.storage.local.get([plan.key], (data) => {
    if (data[plan.key]) renderSet(data[plan.key]);
  });

  pickBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    if (file.size > MAX_BYTES) {
      setStatus(`${plan.label}: 画像が大きすぎます（4MBまで）`, "error");
      fileInput.value = "";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      chrome.storage.local.set({ [plan.key]: reader.result }, () => {
        renderSet(reader.result);
        setStatus(`${plan.label} を登録しました ✓`, "ok");
      });
    };
    reader.onerror = () => setStatus("画像の読み込みに失敗しました", "error");
    reader.readAsDataURL(file);
    fileInput.value = "";
  });

  clearBtn.addEventListener("click", () => {
    chrome.storage.local.remove(plan.key, () => {
      renderUnset();
      setStatus(`${plan.label} の画像を削除しました`, "ok");
    });
  });
});

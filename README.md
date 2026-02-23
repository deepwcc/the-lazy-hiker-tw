# Taiwan Hiking Form Filler 🏔️

這是一個自動填寫台灣國家公園入園申請表（[hike.taiwan.gov.tw](https://hike.taiwan.gov.tw)）的工具。旨在節省申請時重複輸入成員資料的時間，減少手打錯誤。

⚠️ **本工具不會自動提交表單，也不會破解驗證碼 (reCAPTCHA)。**

---

## 🔍 功能特色

*   **自動填表**：自動填寫隊伍、行程、領隊、隊員及留守人資料。
*   **支援多種路線**：內建玉山、桃山、雪山等多種申請範本。
*   **手動最後確認**：腳本填寫完畢後，您仍可手動檢查資料、輸入驗證碼並自行點擊提交。

---

## 🚫 不支援的功能

*   ❌ **不自動提交**：保留最後確認權給使用者。
*   ❌ **不破解驗證碼**：您仍需手動輸入 reCAPTCHA。
*   ❌ **不保證入園**：入園審核由各國家公園管理處決定。

---

## 🛠️ 安裝與準備

### 1. 取得專案
```bash
git clone https://github.com/deepwcc/the-lazy-hiker-tw.git
cd the-lazy-hiker-tw
```

### 2. 安裝 Node.js 依賴 (核心自動化套件)
本工具的核心是基於 Playwright 運作。
```bash
npm install
npx playwright install chromium
```

### 3. 設定申請資料
將範本檔案複製為 `application.json` 並填入您的實際資料：
```bash
cp src/application.桃山單攻.sample.json src/application.json
# 或者使用其他範本
# cp src/application.玉山主東兩天.sample.json src/application.json
```
請編輯 `src/application.json`，將其中的個人資料（姓名、證號、生日、聯絡電話等）替換為實際內容。

---

## 🚀 如何執行

您可以透過 Python (建議) 或直接使用 Node.js 來啟動工具。

### 方法 A：透過 Python 執行 (推薦)
1. 安裝 PyExecJS：
   ```bash
   pip install PyExecJS
   ```
2. 執行：
   ```bash
   python main.py
   ```

### 方法 B：直接使用 Node.js 執行
```bash
node src/apply.js
```

---

## 📄 授權 (License)

[MIT License](LICENSE)

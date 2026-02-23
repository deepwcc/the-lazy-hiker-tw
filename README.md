# Taiwan Hiking Form Filler 🏔️

這是一個自動填寫台灣國家公園入園申請表（[hike.taiwan.gov.tw](https://hike.taiwan.gov.tw)）的工具。旨在節省申請時重複輸入成員資料的時間，減少手打錯誤。

⚠️ **本工具不會自動提交表單，也不會破解驗證碼 (reCAPTCHA)。**

---

## 🔍 功能特色

*   **自動填表**：自動填寫隊伍、行程、領隊、隊員及留守人資料。
*   **目前支援路線**：目前僅完整支援 **玉山單攻** 選項。
*   **手動最後確認**：腳本填寫完畢後，您仍可手動檢查資料、輸入驗證碼並自行點擊提交。

---

## 📝 TODO List (待修復範本)

以下路線範本目前尚未修復，歡迎提交 Pull Request：
- [ ] 桃山單攻
- [ ] 玉山主東兩天
- [ ] 雪山主東三天

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

目前僅支援 **玉山單攻**，請先編輯範本檔案並填入您的實際資料：
1.  開啟 `samples/application.玉山單攻.sample.json`。
2.  將其中的個人資料（姓名、證號、生日、聯絡電話等）替換為實際內容。
3.  儲存檔案。

*(註：原本的 `cp ... src/application.json` 已不再需要，`main.py` 會引導您選擇範本。)*

---

## 🚀 如何執行

1. 安裝 PyExecJS：
   ```bash
   pip install PyExecJS
   ```
2. 執行：
   ```bash
   python main.py
   ```
   *執行後，請從選單中選擇 `玉山單攻 (application.玉山單攻.sample.json)`。*

---

## 📄 授權 (License)

[MIT License](LICENSE)

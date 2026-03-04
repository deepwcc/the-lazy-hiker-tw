# Taiwan Hiking Form Filler 🏔️

這是一個自動填寫台灣國家公園入園申請表（[hike.taiwan.gov.tw](https://hike.taiwan.gov.tw)）的工具。旨在節省申請時重複輸入成員資料的時間，減少手打錯誤。

⚠️ **本工具不會自動提交表單，也不會破解驗證碼 (reCAPTCHA)。**

---

## 🔍 功能特色

*   **自動填表**：自動填寫隊伍、行程、領隊、隊員及留守人資料。
*   **目前支援路線**：目前支援 **玉山主東兩天**、**桃山單攻**、**雪山主東三天**、**聖稜線O型** 等選項。
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

### 2. 安裝 Python 依賴 (核心自動化套件)
本工具的核心是基於 Playwright Python 運作。
```bash
pip install playwright
playwright install chromium
```

### 3. 設定申請資料

為了保護您的個人隱私，請勿直接修改 `samples/` 資料夾下的範本檔案。請按照以下步驟操作：

1.  **複製範本**：將 `samples/application.玉山主東兩天.sample.yaml` 複製為 `application.yaml` (此檔名已被加入 `.gitignore`，不會被上傳到 GitHub)。
    ```bash
    cp samples/application.玉山主東兩天.sample.yaml application.yaml
    ```
2.  **填寫資料**：編輯 `application.yaml`，將其中的個人資料（姓名、證號、生日、聯絡電話等）替換為實際內容。
3.  **執行腳本**：目前 `main.py` 仍預設讀取範本，建議執行時手動指定資料路徑（詳見下述）。

> 💡 **重要提醒**：請務必檢查 `.gitignore` 檔案中是否包含 `application.yaml` 或其他包含個資的檔案路徑，避免意外將敏感資訊推送到公開倉庫。

---

## 🚀 如何執行

1. 執行：
   ```bash
   python main.py
   ```
   *腳本會優先讀取根目錄下的 `application.json`。若找不到，則會引導您從 `samples/` 中選擇範本。*

2. 執行測試：
   ```bash
   # 執行所有測試範本
   python test_apply.py --all
   
   # 依關鍵字篩選測試範本
   python test_apply.py --filter 玉山
   ```

---

## Credits / 致謝

本專案啟發自並參考了 [taiwan-hiking-form-filler](https://github.com/hiiamyes/taiwan-hiking-form-filler) 的設計與邏輯。感謝原作者 [hiiamyes](https://github.com/hiiamyes) 的貢獻。

---

## ⚠️ 免責聲明與法律警告 (Disclaimer & Legal Warning)

### 1. 法律責任說明
本專案僅供 **程式開發技術交流與學術研究** 之用。使用者在執行自動化腳本時，必須遵守中華民國法律（或其他所在地法律）。若因使用本工具導致以下法律問題，使用者須自行承擔全責，開發者概不負責：

*   **《刑法》第 360 條 (妨害電腦使用罪)**：若因頻率控制不當導致目標網站系統癱瘓、運行中斷，可能觸法。
*   **偽造文書罪**：若使用本工具填寫虛假身分證字號、姓名或偽造證明文件以獲取不正當利益（如搶占名額、抽籤），將涉及法律訴訟。
*   **行政規章**：使用自動化程式可能違反「臺灣登山申請一站式服務網」之服務條款，官方有權撤銷申請資格並封鎖帳號。

### 2. 公平性原則
本工具之目的為「輔助」填表，而非「插隊」或「作弊」。強烈建議：

*   **嚴禁** 用於商業營利或大規模代搶名額。
*   **請勿** 繞過網站設置的驗證碼（CAPTCHA）或其他安全防護機制。
*   **請設定合理的 延遲時間（Delay）**，模擬真人操作，避免對政府伺服器造成不必要的負擔。

### 3. 個人資料保護
本工具處理之資料包含身分證字號、手機號碼、緊急聯絡人等高度敏感個資：

*   使用者應確保已獲得所有隊員之明確授權。
*   **安全警告**：請勿將包含真實個資的 json、env 或 config 檔案推送到 GitHub 任何公開分支，否則後果自負。

---

## 📄 授權 (License)

本專案採非商業性使用授權。
- **禁止商業行為**：嚴禁任何形式的營利代辦或商業化使用。

詳情請參閱 [LICENSE](LICENSE) 檔案。

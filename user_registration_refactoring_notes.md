# 使用者註冊邏輯 Domain 層重構說明紀錄

## 1. 背景與重構目標
為了提升系統程式碼的可維護性、可測試性與模組化架構，我們將原本分散在 Flask 路由處理函式（`app.py`）與表單驗證中的「使用者註冊業務規則與初始資料邏輯」獨立抽離至 **Domain（領域）層**。

重構的核心原則：
- **純 Python 實作**：Domain 層不導入 Flask、SQLAlchemy 或任何資料庫模組。
- **高可測試性**：無需啟動 Web 伺服器或建立資料庫即可進行全套邏輯的單元測試。
- **職責單一**：Web 層（`app.py`）僅負責 HTTP 請求接收與回應處理，Domain 層（`domain.py`）專心負責業務驗證與初始資料建構。

---

## 2. 主要修改與檔案結構

```
CPBL/
├── domain.py                     # [新增] 純 Python 領域層（業務驗證與初始狀態判定）
├── tests/
│   └── test_domain.py            # [新增] Domain 層無資料庫單元測試
├── app.py                        # [修改] 呼叫 domain.py 進行註冊，移除內嵌驗證邏輯
├── pyproject.toml                # [修改] 設定 pytest pythonpath = "."
└── user_registration_refactoring_notes.md  # [新增] 本說明文件
```

### 2.1 [domain.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/domain.py) 領域層設計
- **`UserRegistrationResult` 資料結構**：
  - `is_valid: bool`：驗證是否完全通過。
  - `errors: List[str]`：未通過時的錯誤訊息列表。
  - `email`, `username`, `social_link`, `password`：正規化與清理後的欄位資料。
  - `initial_status: str`：初始帳號狀態（預設為 `"active"`）。
  - `default_rewards: Dict[str, Any]`：新註冊使用者的預設獎勵（包含 `welcome_bonus_points: 100` 與 `free_listing_credits: 3`）。
- **`validate_and_build_user()` 驗證函式**：
  - Email：自動去除前後空白並轉為小寫，驗證標準 Email 格式及重複性。
  - 密碼：驗證非空、長度檢查以及二次密碼輸入一致性。
  - Username：若未輸入，自動由 Email 帳號前綴推導生成。
  - Social Link：若未輸入，自動產生預設的 Facebook 社群網址格式。

### 2.2 [app.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/app.py) Web 路由解耦
- 修改 `/register` (HTML Form 註冊) 與 `/api/register` (JSON REST API 註冊) 路由：
  1. 擷取請求欄位與資料庫重複檢查標籤（`email_exists`, `username_exists`）。
  2. 傳入 `domain.validate_and_build_user()` 取得 `UserRegistrationResult`。
  3. 若 `is_valid` 為 `False`，前端頁面 Flash 顯示錯誤訊息或 API 回傳 HTTP 400 錯誤。
  4. 若 `is_valid` 為 `True`，直接使用正規化後的資料建立 `User` ORM 物件並 Commit 至資料庫。

### 2.3 [tests/test_domain.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/tests/test_domain.py) 獨立單元測試
- 包含 8 個獨立單元測試案例：
  - `test_valid_user_registration_defaults`: 測試成功註冊與預設值推導。
  - `test_user_registration_explicit_fields`: 測試自訂欄位處理。
  - `test_invalid_email_format`: 測試不合規 Email 阻擋。
  - `test_missing_required_fields`: 測試空欄位檢測。
  - `test_short_password`: 測試過短密碼阻擋。
  - `test_mismatched_password_confirm`: 測試二次密碼不一致阻擋。
  - `test_duplicate_email_flag`: 測試重複 Email 標籤處理。
  - `test_duplicate_username_flag`: 測試重複 Username 標籤處理。

---

## 3. 測試驗證結果

使用 `uv run pytest` 執行全套測試，結果如下：

- **`tests/test_domain.py`**：8 passed (耗時僅 0.02 秒)
- **`test_app.py`**：4 passed
- **總計 12 個測試全數通過** ✅

# Context Comparison: Registration Password Length Validation Rule Change

本文件比較在系統進行分層架構重構前後，若欲將「使用者註冊密碼最小長度由 8 字元調整為 10 字元」時，在兩版 codebase 中的程式碼修改位置與責任邊界劃分。

## 註冊密碼長度規則修改位置比較表

| 比較項目 | 基線版本 (Baseline) | 重構完成版本 (Day 3 Refactored) |
| :--- | :--- | :--- |
| **主要修改檔案** | [forms.py](file:///d:/2026上課/CPBL/forms.py) 及 [app.py](file:///d:/2026上課/CPBL/app.py) | [domain.py](file:///d:/2026上課/CPBL/domain.py) |
| **修改位置與行號** | `forms.py:RegistrationForm` (L46) `password` 欄位驗證器；及 `app.py:register` (L41) | `domain.py:validate_and_build_user()` (L89-L91) |
| **修改之函式／類別／常數** | `RegistrationForm.password` (WTForms `Length` validator) | `validate_and_build_user` (Pure Python Domain Function) |
| **修改原因說明** | 重構前驗證邏輯散落在 Web 表單框架 (WTForms) 與 Route 處理流程中，缺乏單一領域邏輯擁有者，修改時需在 Flask UI 表單驗證器層新增長度限制。 | 重構後驗證邏輯完全集中於純 Python Domain 層，Route 與 Application Use Case 不含任何格式或長度檢查規則，修改單一 Domain 函式即可生效。 |
| **改動影響範圍** | 需同時關心 WTForms 與 Route HTTP 請求處理流程。 | 僅影響 Domain 業務規則，可在零 Flask/資料庫依賴下獨立進行單元測試。 |

---

## 結論與問答

**問題：重構後，使用者註冊驗證規則是否有更明確的擁有者？**

> 重構後，使用者註冊驗證規則擁有了極為明確且唯一的擁有者——純 Python 實作的 Domain 層（`domain.py` 中的 `validate_and_build_user` 函式與 `RegistrationResult` 領域物件）。

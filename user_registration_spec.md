# User Registration Specification

## User story
作為訪客，我希望能夠輸入 Email、密碼與顯示名稱來註冊新帳號，以便使用系統個人化服務。

## Rules
- **必填欄位**：`email`、`password`、`confirm_password`、`display_name`。
- **Email 格式與唯一性**：
  - 必須符合標準 Email 格式。
  - 自動去除前後空白，字母一律轉小寫儲存。
  - 若 Email 已存在，阻擋註冊並顯示提示：「此 Email 已被註冊」。
- **密碼規則**：
  - 長度須介於 8 ~ 32 個字元。
  - 必須包含至少一個大寫英文字母、一個數字。
  - `confirm_password` 必須與 `password` 一致。
- **安全性**：
  - 後端必須使用 Bcrypt 對密碼進行加鹽 Hash 處理，嚴禁明碼存入資料庫。
- **回應與轉向**：
  - 註冊成功後回傳 HTTP 201，自動登入並轉向至 `/dashboard`。

## Acceptance examples
| Email | Password | Confirm Password | Display Name | 預期結果 | 訊息 / 狀態碼 |
|---|---|---|---|---|---|
| `user@example.com` | `Pass1234` | `Pass1234` | 小明 | 註冊成功 | HTTP 201 (轉向 /dashboard) |
| ` USER@example.com ` | `Pass1234` | `Pass1234` | 小明 | 註冊成功 | 自動轉小寫並去空白 |
| `invalid-email` | `Pass1234` | `Pass1234` | 小明 | 阻擋提交 | 請輸入有效的 Email 格式 |
| `user@example.com` | `12345` | `12345` | 小明 | 阻擋提交 | 密碼至少需 8 個字元且包含大寫與數字 |
| `user@example.com` | `Pass1234` | `Different12` | 小明 | 阻擋提交 | 兩次輸入的密碼不一致 |
| *(已存在之 Email)* | `Pass1234` | `Pass1234` | 小明 | 註冊失敗 | 此 Email 已被註冊 |

## Done when
- 所有 Acceptance Examples 均有寫入單元測試 / 整合測試且通過。
- Agent 須提出 DB Schema（Users Table）變更說明及密碼加密方式。
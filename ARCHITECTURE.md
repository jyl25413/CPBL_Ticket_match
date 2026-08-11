# CPBL 專案分層架構設計規範 (ARCHITECTURE.md)

本專案採用 **Hexagonal Architecture (Ports & Adapters)** 與 **Clean Architecture** 分層原則，確保「業務規則有擁有者，候選來源可替換，依賴方向單向依附」。

---

## 1. 架構與依賴規範表

| 模組 (檔案) | 擁有的責任 | 主要輸入 / 輸出 | 允許依賴 | 禁止依賴 | 程式碼實作證據 |
|---|---|---|---|---|---|
| **Domain**<br>(`domain.py`) | 企業核心業務規則驗證、格式檢查、狀態判定與例外定義 | 原生型態 (str, int) → Validation Result / Exception | Python 標準庫 (`dataclasses`, `re`, `typing`) | **嚴禁** Web 框架、ORM/DB、外部 SDK 或 Ports/Adapters | [domain.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/domain.py)<br>- `validate_username()`<br>- `validate_and_build_user()` |
| **Ports**<br>(`ports.py`) | 定義領域外圍抽象介面契約 (ABC) | 抽象方法定義 | Domain 實體 | Adapters、Web 框架、具體 ORM / 資料庫 | [ports.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/ports.py)<br>- `UserRepositoryPort`<br>- `UsernameSuggesterPort`<br>- `UserRepository`<br>- `EmailService` |
| **Application**<br>(`application.py`) | 用戶案例 (Use Case) 流程編排、呼叫 Port 介面與 Validation Boundary | DTO / 原始參數 → Dictionary 執行結果 | Domain、Ports | Adapters 具體類別、Web 框架、SQL / ORM 查詢 | [application.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/application.py)<br>- `RegisterUsernameUseCase`<br>- `RegisterUserUseCase` |
| **Adapters**<br>(`adapters.py`) | 實作 Ports 介面，處理資料庫存取 (SQLAlchemy / InMemory) 與外部服務 | Domain / 傳入參數 → ORM 模型 / 替代 ID 候選清單 | Domain、Ports、SQLAlchemy、外部套件 | Web 路由、Application Use Cases | [adapters.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/adapters.py)<br>- `SqlAlchemyUserRepository`<br>- `RuleBasedUsernameSuggester`<br>- `InMemoryUserRepository` |
| **Route**<br>(`app.py`) | 展示層：接收 HTTP Request、注入 Adapter 至 UseCase、回傳 Response | HTTP Request → JSON / HTML Template | Application、Adapters | Domain 直接呼叫、直接 ORM/DB 操作 (`db.session`) | [app.py](file:///d:/2026%E4%B8%8A%E8%AA%B2/CPBL/app.py)<br>- `register()`<br>- `api_register()` |

---

## 2. 替代 ID 推薦功能責任劃分設計

```mermaid
graph TD
    Client[前端 / HTTP Request] --> Route[app.py: Web Route]
    Route --> App[application.py: RegisterUsernameUseCase]
    App --> Domain[domain.py: validate_username]
    App --> Adapter[adapters.py: RuleBasedUsernameSuggester]
    App --> Repo[adapters.py: UserRepositoryPort]
    
    subgraph Validation Boundary (驗證邊界)
        Adapter -->|產出原始候選 ID| Filter[雙重過濾: 格式合規 + DB未佔用]
        Filter -->|保證100%可註冊| Recommendations[回傳 3 個推薦 ID]
    end
```

1. **流程編排（Application）**：`RegisterUsernameUseCase.execute()` 先對輸入進行 Domain 格式驗證，若被佔用則呼叫 Suggester 取得候選 ID，並執行驗證邊界。
2. **候選來源（Adapter）**：`RuleBasedUsernameSuggester.suggest()` 作為可替換之轉接器，僅專注產出潛在 ID，不關心 DB 狀態。
3. **驗證邊界（Validation Boundary）**：UseCase 確保所有來自 Adapter 的候選 ID **必須通過 `validate_username()` 格式驗證**，且 **`not user_repo.exists_by_username()` 資料庫可用性檢查**，保證傳回前端的推薦 ID 100% 可被成功註冊。

# Oncology Weekly Trend Reporter

自動生成腫瘤科每週治療趨勢報告，以繁體中文撰寫（英文醫學名詞不翻譯）。

目前設定：**乳癌（Breast Cancer）**

資料來源：OpenEvidence AI · OncDaily RSS · OncLive · ESMO · ClinicalTrials.gov

週報範例：[2026-W16](https://github.com/htlin222/breast-cancer-uptodate/wiki/2026-W16)

---

## 快速開始

```bash
# 安裝 uv（Python 套件管理）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝相依套件
uv sync

# 執行爬蟲 + 報告（OncDaily / OncLive / ESMO）
uv run python main.py scrape

# 生成報告（需手動補充 OpenEvidence 段落，或直接在 Claude Code 中執行）
uv run python main.py report
```

報告輸出至 `reports/YYYY-Wxx.md`，push 到 `main` 後 GitHub Actions 自動發布至 Wiki。

---

## 專案結構

```
.
├── source/                   ← 所有可調整參數（不需改 Python）
│   ├── keywords.yml          ← 疾病相關關鍵詞（過濾用）
│   ├── drug_groups.yml       ← 藥物分組 + 會議關鍵詞
│   ├── search_queries.yml    ← Twitter 搜尋 query
│   ├── web_sources.yml       ← 爬蟲來源（RSS URL、Google News site）
│   └── twitter.yml           ← GraphQL op_id、cookie skip 清單
├── config/
│   └── seeds.txt             ← KOL Twitter 帳號種子清單
├── src/
│   ├── config.py             ← YAML 載入器（lru_cache）
│   ├── webscraper.py         ← 網路爬蟲（driven by web_sources.yml）
│   ├── fetcher.py            ← Twitter 爬蟲（driven by twitter.yml）
│   ├── reporter.py           ← 推文聚合報告生成
│   ├── discover.py           ← KOL 自動發掘
│   └── db.py                 ← SQLite 儲存
├── reports/                  ← 產出的週報（push 即觸發 wiki 發布）
├── main.py                   ← CLI 入口
└── .github/workflows/
    └── publish-wiki.yml      ← 自動發布 wiki 的 GitHub Action
```

---

## 切換到其他癌症 / 血液腫瘤

本系統設計為**癌症無關（cancer-agnostic）**，所有領域知識都集中在 `source/` 下的 YAML 檔案，切換癌種只需修改這五個檔案，**不需動任何 Python 程式碼**。

### 步驟 1 — 替換 `source/keywords.yml`

```yaml
# 以瀰漫性大 B 細胞淋巴瘤（DLBCL）為例
breast_cancer_keywords:       # ← 改這個 key 的值（key 名稱不重要）
  - DLBCL
  - diffuse large B-cell lymphoma
  - rituximab
  - R-CHOP
  - polatuzumab vedotin
  - Polivy
  - CAR-T
  - axicabtagene
  - lisocabtagene
  - loncastuximab
  - tafasitamab
  - Monjuvi
  - bispecific
  - epcoritamab
  - glofitamab
  - BCL2
  - venetoclax
  - PI3K delta
  - CD19
  - CD20
  - POLARIX
  - L-MIND
```

### 步驟 2 — 替換 `source/drug_groups.yml`

依新癌種重寫藥物分組：

```yaml
drug_groups:
  Anti-CD20:
    - rituximab
    - obinutuzumab
    - Gazyva
  CAR-T:
    - axicabtagene
    - lisocabtagene
    - axi-cel
    - liso-cel
    - ZUMA
    - TRANSFORM
  Bispecific antibodies:
    - epcoritamab
    - glofitamab
    - mosunetuzumab
  BCL2 inhibitors:
    - venetoclax
    - Venclyxto

conference_keywords:
  - ASH
  - ASCO
  - EHA
  - ICML
  - abstract
  - "#ASH"
  - "#EHA"
```

### 步驟 3 — 替換 `source/search_queries.yml`

```yaml
search_queries:
  - "(DLBCL OR diffuse large B-cell) (R-CHOP OR polatuzumab OR CAR-T)"
  - "(DLBCL) (CAR-T OR axicabtagene OR lisocabtagene OR ZUMA OR TRANSFORM)"
  - "(lymphoma) (bispecific OR epcoritamab OR glofitamab OR mosunetuzumab)"
  - "(DLBCL OR lymphoma) (FDA OR approval OR OS OR PFS OR abstract)"
  - "(diffuse large B cell lymphoma) lang:en"
```

### 步驟 4 — 替換 `source/web_sources.yml`（選擇性）

大部分來源（OncLive、ESMO）本身就涵蓋血液腫瘤，只需調整 Google News 搜尋字串：

```yaml
sources:
  - name: OncDaily
    type: rss
    url: "https://oncodaily.com/oncolibrary/hematology/feed/"   # ← 改路徑
    max_items: 20
    bc_filter: false

  - name: OncLive
    type: google_news
    domain: onclive.com
    max_items: 30
    noise_filter: null
    # Google News query 自動為 "site:onclive.com breast cancer"
    # 改為 DLBCL 需修改 webscraper.py 中的 q= 字串
    # 或在 web_sources.yml 加 query 欄位（見下方進階說明）

  - name: ASH News
    type: google_news
    domain: hematology.org
    max_items: 20
    noise_filter: "membership|about|contact|award|meeting registration"
```

#### 進階：自訂 Google News 查詢字串

在 `web_sources.yml` 加 `query` 欄位，`webscraper.py` 會優先使用：

```yaml
  - name: OncLive
    type: google_news
    domain: onclive.com
    query: "DLBCL OR lymphoma"    # ← 覆蓋預設的 "breast cancer"
    max_items: 30
```

並在 `src/webscraper.py` 的 `_fetch_google_news` 函式中讀取：

```python
query_term = src.get("query", "breast cancer")  # 一行改動
q = f"site:{domain} {query_term}"
```

### 步驟 5 — 替換 `config/seeds.txt`

```
# DLBCL / Hematology KOLs
JasonHAlderma    # Jason Westin, MD Anderson
LorenzoCerchiett # Lorenz Cerchione
seemaasst        # Seema Ansari
lymphomainfo     # Lymphoma Research Foundation
ASHhematology    # American Society of Hematology
```

### 步驟 6 — 改報告標題（選擇性）

`main.py` 的 `cmd_scrape` 與 `src/reporter.py` 中的標題字串可直接改。

---

## 常見維護任務

| 問題 | 解法 |
|------|------|
| Twitter API 回 404 | 更新 `source/twitter.yml` 的 `op_id` |
| 某新藥沒被捕捉 | 加進 `source/keywords.yml` 和對應 `drug_groups.yml` |
| 新增爬蟲來源 | 在 `source/web_sources.yml` 加一筆 `type: rss` 或 `type: google_news` |
| 查詢字串太雜 | 修改 `source/search_queries.yml` |
| Wiki 沒更新 | 確認 push 路徑含 `reports/*.md`；或手動跑 Actions → `workflow_dispatch` |

---

## GitHub Actions — Wiki 自動發布

每次 push 包含 `reports/*.md` 的 commit 到 `main`，`.github/workflows/publish-wiki.yml` 自動：

1. 把新報告複製到 wiki repo
2. 重建 `Home.md` 索引（最新在前）
3. Force-push 到 wiki `master` branch

手動觸發：Actions → **Publish Reports to Wiki** → **Run workflow**

---

## 授權

MIT

# Oncology Weekly Trend Reporter

自動生成腫瘤科每週治療趨勢報告，以繁體中文撰寫（英文醫學名詞不翻譯）。

支援癌別：**乳癌（Breast）** · **肺癌（Lung）** · **大腸直腸癌（Colorectal）**

資料來源：OpenEvidence AI · OncDaily RSS · OncLive · ESMO · ClinicalTrials.gov · CrossRef

---

## 快速開始

```bash
# 安裝 uv（Python 套件管理）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝相依套件
uv sync

# 查看支援的癌別
uv run python main.py list-cancers

# 執行爬蟲 + 報告（指定癌別）
uv run python main.py scrape --cancer lung
uv run python main.py journals --cancer lung
uv run python main.py report --cancer lung

# 或一次跑完整個 pipeline
uv run python main.py run --cancer breast
```

報告輸出至 `reports/<cancer>/YYYY-Wxx.md`，push 到 `main` 後 GitHub Actions 自動發布至 Wiki。

---

## 使用方式

所有指令都支援 `--cancer <type>` 參數（預設 `breast`）：

```bash
uv run python main.py <command> --cancer <type>
```

| 指令 | 說明 |
|------|------|
| `setup` | 設定 Twitter cookies |
| `fetch` | 從追蹤的 KOL 抓取推文 |
| `discover` | 從推文中發現新 KOL |
| `scrape` | 爬取醫學新聞網站 |
| `journals` | 透過 CrossRef API 抓取期刊論文 |
| `report` | 生成每週 Markdown 報告 |
| `run` | 依序執行 fetch → discover → scrape → journals → report |
| `accounts` | 列出追蹤中的帳號 |
| `list-cancers` | 顯示所有可用癌別 |

---

## 專案結構

```
.
├── source/
│   ├── _shared/                  ← 共用設定（Twitter API config）
│   │   └── twitter.yml
│   ├── breast/                   ← 乳癌設定
│   │   ├── keywords.yml          ← 疾病關鍵詞
│   │   ├── drug_groups.yml       ← 藥物分組 + 會議關鍵詞
│   │   ├── search_queries.yml    ← Twitter 搜尋語句
│   │   ├── web_sources.yml       ← 爬蟲來源
│   │   ├── journals.yml          ← CrossRef 期刊設定
│   │   └── seeds.txt             ← KOL 種子帳號
│   ├── lung/                     ← 肺癌設定（同上結構）
│   └── colorectal/               ← 大腸直腸癌設定（同上結構）
├── src/
│   ├── config.py                 ← YAML 載入器（支援癌別切換）
│   ├── webscraper.py             ← 網路爬蟲
│   ├── crossref_fetcher.py       ← CrossRef 期刊抓取
│   ├── fetcher.py                ← Twitter 爬蟲
│   ├── reporter.py               ← 報告生成
│   ├── discover.py               ← KOL 自動發掘
│   └── db.py                     ← SQLite 儲存（per-cancer）
├── data/
│   └── <cancer>/                 ← 各癌別的快取資料
│       ├── tweets.db
│       ├── webscrape_cache.json
│       └── journals_cache.json
├── reports/
│   ├── breast/                   ← 乳癌週報
│   ├── lung/                     ← 肺癌週報
│   └── colorectal/               ← 大腸直腸癌週報
├── main.py                       ← CLI 入口
├── CLAUDE.md                     ← Claude Code 報告生成指引
└── .github/workflows/
    └── publish-wiki.yml          ← Wiki 自動發布
```

---

## 新增癌別

本系統設計為**癌別無關（cancer-agnostic）**。新增追蹤癌別只需：

1. 在 `source/` 下建立新資料夾（如 `source/gastric/`）
2. 複製任一現有癌別的 YAML 檔案作為模板
3. 修改關鍵詞、藥物分組、搜尋語句、爬蟲來源、期刊清單
4. 驗證：`uv run python main.py list-cancers`
5. 執行：`uv run python main.py run --cancer gastric`

**不需修改任何 Python 程式碼。**

---

## 常見維護任務

| 問題 | 解法 |
|------|------|
| Twitter API 回 404 | 更新 `source/_shared/twitter.yml` 的 `op_id` |
| 某新藥沒被捕捉 | 加進 `source/<cancer>/keywords.yml` 和 `drug_groups.yml` |
| 新增爬蟲來源 | 在 `source/<cancer>/web_sources.yml` 加一筆 |
| Wiki 沒更新 | 確認 push 路徑含 `reports/**/*.md`；或手動跑 workflow_dispatch |

---

## 授權

MIT

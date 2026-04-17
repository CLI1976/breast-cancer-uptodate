# CLAUDE.md — Breast Cancer Weekly Report

## Project Purpose

Auto-generate weekly Markdown reports on breast cancer treatment trends from:
- OpenEvidence MCP (`mcp__openevidence__oe_ask`)
- PubMed MCP (`mcp__claude_ai_PubMed__search_articles`)
- ClinicalTrials.gov MCP (`mcp__claude_ai_Clinical_Trials__search_trials`)
- CrossRef API (via `python main.py journals`)
- Web news (OncDaily RSS, OncLive/ESMO via Google News RSS)

---

## Before Writing a New Report

**MANDATORY — do this BEFORE writing a single word of content:**

```bash
# 1. Find the latest report
PREV=$(ls reports/ -t | head -1)
echo "Previous report: $PREV"

# 2. Read it fully — note every trial, drug approval, and section topic covered
# 3. Grep key trial names to see what's already documented
grep -E "DESTINY-Breast|ASCENT|NATALEE|monarchE|VIKTORIA|EMBER|TROPION|INAVO|SERENA" reports/$PREV
```

After reading the previous report, answer these before writing:
- Which trials were already covered with final/mature data? → **skip entirely**
- Which trials had interim data last week? → include only if new follow-up published
- Which drug approvals were already documented? → **skip unless label expanded**

**Do NOT repeat** any finding with identical numbers. Mark new follow-up data explicitly: `[更新]` before the subsection heading, and state what changed vs last week.

If a section has no genuinely new data this week: write `_本週無新訊號_` and move on.

---

## Report File Naming

```
reports/YYYY-WNN.md
```

Use ISO week number: `python3 -c "from datetime import date; d=date.today(); print(f'{d.year}-W{d.isocalendar()[1]:02d}')"`.

---

## Report Structure

### Required Sections (繁體中文)

```
# 乳癌治療趨勢週報 — YYYY-WNN

> 生成日期：YYYY-MM-DD｜資料來源：...
> 涵蓋期間：...

---

## 摘要
（本週五大訊號 — bullet points, concrete numbers）

## 一、HER2 靶向治療
## 二、ADC 在 TNBC
## 三、HR+/HER2− 內分泌治療
## 四、CDK4/6 Inhibitor：輔助治療確立
## 五、PARP Inhibitor 與 BRCA 族群
## 六、免疫治療 (TNBC)
## 七、早期乳癌：手術、放療、風險分層
## 八、進行中高優先試驗追蹤
## 九、台灣臨床情境備註
## 十、本週 Key Takeaways

## 十一、蜥蜴LLM 點評
（OpenEvidence分類：practice-changing vs hypothesis-generating）

## 十二、媒體動態
（OncDaily / OncLive / ESMO news table）

## 文獻速報 — CrossRef 期刊
（LLM-filtered JCO articles）
```

Sections without new data this week should say: `_本週無新訊號_`

---

## Writing Style

- Language: **繁體中文**，英文術語保留原文（T-DXd, HR, PFS, iDFS 等）
- Every clinical claim must cite trial name + author + journal + DOI
- Tables: use Markdown tables for comparative data (trial vs control arm)
- Numbers: always include HR, CI, p-value when available
- Avoid vague superlatives; every "significant" needs a number

---

## Data Pipeline

Run in order before writing:

```bash
uv run python main.py scrape          # OncDaily + OncLive + ESMO news
uv run python main.py journals        # JCO CrossRef (keyword pre-screened)
```

For full pipeline (including Twitter if credentials available):

```bash
uv run python main.py run
```

Cached data locations:
- `data/webscrape_cache.json` — web news articles
- `data/journals_cache.json` — CrossRef journal articles (pre-screened, not yet final-filtered)

**CrossRef filtering note:** The Python fetcher applies a keyword pre-screen only (broad net).
When writing the report, read `data/journals_cache.json` and **filter in-session** — discard any
article whose primary topic is not breast cancer (e.g. gastroesophageal articles that share HER2).
Only include articles confirmed breast-cancer-relevant in the `## 文獻速報` section.

---

## 蜥蜴LLM 點評 Section

Use `mcp__openevidence__oe_ask` with a prompt like:

```
Based on the following breast cancer findings from this week, classify each as:
- Practice-changing (changes standard of care NOW)
- Hypothesis-generating (promising but needs confirmation)
- Context-dependent (changes practice for specific subgroup only)

[list findings with trial names and key numbers]
```

Extract result with: `result.extracted_answer_raw`

---

## After Writing

1. Check word count: report should be 3000–8000 words
2. Verify every table has header separators (`|---|---|`)
3. Run `uv run python main.py report` if auto-generating from DB
4. Commit: `git add reports/YYYY-WNN.md && git commit -m "report: YYYY-WNN"`
5. Push → GitHub Action auto-publishes to Wiki

---

## Duplicate-Avoidance Checklist

Before finalising, cross-check against the previous report:

```bash
PREV=$(ls reports/ -t | head -2 | tail -1)
# Check trial names
grep -E "DESTINY-Breast|ASCENT|NATALEE|monarchE|VIKTORIA|EMBER|TROPION|INAVO|SERENA" reports/$PREV
# Check HR/PFS numbers — if same numbers appear, it's a repeat
grep -E "HR [0-9]|PFS [0-9]|iDFS [0-9]|ORR [0-9]" reports/$PREV | head -20
```

Rules:
- Same trial + same numbers → **delete the section**
- Same trial + new data (updated follow-up, subgroup, approval) → keep with `[更新]` tag
- Brand new trial → include normally

---

## Switching to Another Cancer Type

See `README.md` → "如何切換至其他癌種" for step-by-step instructions (DLBCL example included).

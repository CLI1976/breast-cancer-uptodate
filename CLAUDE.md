# CLAUDE.md — Multi-Cancer Weekly Report

## Project Purpose

Auto-generate weekly Markdown reports on cancer treatment trends from:
- OpenEvidence MCP (`mcp__openevidence__oe_ask`)
- PubMed MCP (`mcp__claude_ai_PubMed__search_articles`)
- ClinicalTrials.gov MCP (`mcp__claude_ai_Clinical_Trials__search_trials`)
- CrossRef API (via `python main.py journals --cancer <type>`)
- Web news (OncDaily RSS, OncLive/ESMO via Google News RSS)

Supported cancer types: **breast**, **lung**, **colorectal**
(add more by creating a new directory under `source/`)

---

## Before Writing a New Report

**MANDATORY — do this BEFORE writing a single word of content:**

```bash
# 1. Determine cancer type (e.g., breast, lung, colorectal)
CANCER=lung   # change as needed

# 2. Find the latest report for this cancer type
PREV=$(ls reports/$CANCER/ -t | head -1)
echo "Previous report: reports/$CANCER/$PREV"

# 3. Read it fully — note every trial, drug, and section topic covered
# 4. Grep key trial names to check what's already documented
grep -E "trial|phase|FDA|approved" reports/$CANCER/$PREV | head -20
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
reports/<cancer>/YYYY-WNN.md
```

Examples:
- `reports/breast/2026-W17.md`
- `reports/lung/2026-W17.md`
- `reports/colorectal/2026-W17.md`

Use ISO week number: `python3 -c "from datetime import date; d=date.today(); print(f'{d.year}-W{d.isocalendar()[1]:02d}')"`.

---

## Report Structure

### Required Sections (繁體中文)

The section headings should be tailored to the cancer type. Use the drug groups defined
in `source/<cancer>/drug_groups.yml` as the basis for clinical sections.

```
# <Cancer Type> 治療趨勢週報 — YYYY-WNN

> 生成日期：YYYY-MM-DD｜資料來源：...
> 涵蓋期間：...

---

## 摘要
（本週五大訊號 — bullet points, concrete numbers）

## 一～N、Clinical sections based on drug_groups.yml
（Each drug group in the YAML becomes a report section）

## 進行中高優先試驗追蹤
## 台灣臨床情境備註
## 本週 Key Takeaways

## LLM 點評
（OpenEvidence分類：practice-changing vs hypothesis-generating）

## 媒體動態
（Web news table）

## 文獻速報 — CrossRef 期刊
（LLM-filtered journal articles）
```

Sections without new data this week should say: `_本週無新訊號_`

### Cancer-Specific Section Examples

**Breast cancer:** HER2 靶向治療, ADC 在 TNBC, HR+/HER2− 內分泌治療, CDK4/6 Inhibitor, PARP Inhibitor, 免疫治療, 早期乳癌

**Lung cancer:** EGFR 靶向治療, ALK Inhibitor, KRAS G12C, 其他分子標靶 (RET/ROS1/MET/BRAF), ADC, 免疫治療, 圍手術期治療

**Colorectal cancer:** Anti-EGFR, 免疫治療 (MSI-H/dMMR), BRAF 靶向, Anti-VEGF, HER2 靶向 (CRC), 晚線治療, ctDNA/MRD 導向, 圍手術期治療

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
CANCER=lung   # change as needed

uv run python main.py scrape --cancer $CANCER     # web news
uv run python main.py journals --cancer $CANCER   # CrossRef articles
```

For full pipeline (including Twitter if credentials available):

```bash
uv run python main.py run --cancer $CANCER
```

Cached data locations (per cancer type):
- `data/<cancer>/webscrape_cache.json` — web news articles
- `data/<cancer>/journals_cache.json` — CrossRef journal articles
- `data/<cancer>/tweets.db` — SQLite tweet database

**CrossRef filtering note:** The Python fetcher applies a keyword pre-screen only (broad net).
When writing the report, read `data/<cancer>/journals_cache.json` and **filter in-session** — discard any
article whose primary topic doesn't match the target cancer type.

---

## LLM 點評 Section

Use `mcp__openevidence__oe_ask` with a prompt like:

```
Based on the following [cancer type] findings from this week, classify each as:
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
3. Commit: `git add reports/<cancer>/YYYY-WNN.md && git commit -m "report: <cancer> YYYY-WNN"`
4. Push → GitHub Action auto-publishes to Wiki

---

## Duplicate-Avoidance Checklist

Before finalising, cross-check against the previous report:

```bash
CANCER=lung
PREV=$(ls reports/$CANCER/ -t | head -2 | tail -1)
# Check trial names
grep -E "phase|trial|NCT" reports/$CANCER/$PREV | head -20
# Check HR/PFS numbers — if same numbers appear, it's a repeat
grep -E "HR [0-9]|PFS [0-9]|OS [0-9]|ORR [0-9]" reports/$CANCER/$PREV | head -20
```

Rules:
- Same trial + same numbers → **delete the section**
- Same trial + new data (updated follow-up, subgroup, approval) → keep with `[更新]` tag
- Brand new trial → include normally

---

## Adding a New Cancer Type

1. Create `source/<cancer_name>/` directory
2. Add YAML files: `keywords.yml`, `drug_groups.yml`, `search_queries.yml`, `web_sources.yml`, `journals.yml`, `seeds.txt`
3. Use existing cancer configs as templates
4. Test: `uv run python main.py list-cancers` to verify detection
5. Run: `uv run python main.py scrape --cancer <cancer_name>`

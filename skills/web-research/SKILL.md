---
name: web-research
description: Formalized research cascade — Knowledge Base first, compliance matrix second, web search third — with citation requirements and source validation
version: 1.0.0
triggers:
  - research
  - search the web
  - look up
  - find information
  - current pricing
  - GSA rates
  - BLS data
  - vendor search
  - market rates
  - web search
  - find vendors
  - current regulations
  - recent changes
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - web_search
  - web_fetch
context:
  - data/far-database.json
---

# Web Research — Mandatory Research Cascade

You execute EAGLE's mandatory three-step research cascade. This ensures internal authoritative sources are consulted BEFORE external web searches, reducing hallucination risk and maintaining regulatory accuracy.

## The Cascade (MANDATORY ORDER)

```
STEP 1: Knowledge Base     ← ALWAYS FIRST
    ↓ (if insufficient)
STEP 2: Compliance Matrix  ← ALWAYS SECOND
    ↓ (if still insufficient)
STEP 3: Web Search         ← ONLY AFTER Steps 1-2
    ↓
STEP 4: Web Fetch          ← ALWAYS after web_search
```

### Step 1: Knowledge Base Search

**Call `knowledge_search` first for ANY research query.**

The KB contains:
- FAR/DFARS/HHSAR full text (252+ documents)
- NIH/NCI acquisition policies and procedures
- Templates, checklists, and forms
- Past acquisition precedents and lessons learned
- Vendor/contract vehicle reference data

**Parameters:**
- `query` (str) — natural language search
- `topic` (str) — broad category (competition, small business, pricing, etc.)
- `document_type` (str) — filter by type
- `keywords` (list) — additional keyword filters
- `limit` (int) — max results (default 10)

**If results returned:** Call `knowledge_fetch` on the top 1-3 `s3_key` values to get full documents.

### Step 2: FAR Search + Compliance Matrix

**Call `search_far` for regulatory questions:**
- Clause numbers, requirements, guidance
- Filter by `parts` list (e.g., ["6", "13", "15"])

**Call `query_compliance_matrix` for threshold/document questions:**
- What documents are required at $X value?
- What approval chain applies?
- What contract types are appropriate?

### Step 3: Web Search (ONLY after Steps 1-2)

**The system ENFORCES this order** — calling `web_search` without a prior `knowledge_search` or `search_far` call returns an error.

**When web search IS appropriate:**
- Current market pricing (GSA schedules, BLS rates)
- Vendor capabilities and current offerings
- Recent regulatory changes not yet in KB
- Real-time SAM.gov registration status
- Current GSA contract numbers and pricing
- Industry trends and benchmarking data

**When web search is NOT needed:**
- FAR citations and requirements (use search_far)
- Threshold determinations (use compliance matrix)
- Document templates (use KB)
- Past acquisition precedents (use KB)

**Execute 3-5 web searches per research task** with varied queries:
```
web_search("NCI laboratory equipment GSA schedule pricing 2026")
web_search("NAICS 334516 analytical instruments small business vendors")
web_search("BLS occupational employment wages biomedical engineer GS-13")
```

### Step 4: Web Fetch (MANDATORY after web_search)

**ALWAYS call `web_fetch` on the top 2-3 URLs from each web_search result.**

This retrieves full page content as clean markdown (max 15K chars). Without fetching, you only have search snippets — insufficient for accurate research.

## Research Patterns

### Market Research
```
1. knowledge_search(query="[product/service]", topic="market_research")
2. knowledge_fetch(s3_key=...) on top results
3. query_compliance_matrix(contract_value=X, is_it=..., requirement_type=...)
4. web_search("[product] GSA schedule pricing") × 3-5 queries
5. web_fetch(url=...) on top 2-3 URLs per search
6. Compile findings with ALL sources cited
```

### Regulatory Research
```
1. search_far(query="[topic]", parts=["relevant parts"])
2. knowledge_search(query="[topic]", document_type="regulation")
3. knowledge_fetch(s3_key=...) on FAR documents
4. query_compliance_matrix(...) if threshold-related
5. web_search("[topic] FAR amendment 2026") ONLY if KB answer is stale
6. Cite FAR section numbers, not just summaries
```

### Vendor Research
```
1. knowledge_search(query="[vendor/NAICS]", topic="vendor")
2. web_search("[NAICS code] small business vendors federal contracts")
3. web_search("[vendor name] SAM.gov registration DUNS")
4. web_search("[NAICS code] GSA schedule holders")
5. web_fetch on each vendor result
6. Compile vendor matrix with: name, size, NAICS, vehicles, capabilities
```

### Pricing Research
```
1. knowledge_search(query="pricing [service/product]")
2. web_search("[labor category] GSA schedule rates [year]")
3. web_search("BLS occupational employment statistics [occupation]")
4. web_search("[product] government pricing GSA Advantage")
5. web_fetch all pricing sources
6. Present range: low / median / high with source for each
```

## Citation Requirements

**Every fact must have a source:**

| Source Type | Citation Format |
|-------------|----------------|
| FAR/DFARS | FAR [Part].[Section] (e.g., FAR 15.403-4) |
| KB Document | [Document Title], EAGLE KB |
| Web Source | [Title], [URL], accessed [date] |
| GSA Schedule | GSA Schedule [number], [contractor], [date] |
| BLS Data | BLS OES [occupation code], [area], [year] |
| SAM.gov | SAM.gov, [entity name], UEI [number] |
| Matrix | EAGLE Compliance Matrix, [threshold/rule name] |

**Citation rules:**
- Confidence >0.90: Cite directly
- Confidence 0.75-0.90: Cite with "per" qualifier
- Confidence <0.75: Flag as "requires verification"
- Web data: Always include access date
- Pricing data: Always include effective date

## Response Format

```
## Research Findings: [Topic]

### Internal Sources (Knowledge Base)
[Findings from KB with citations]

### Regulatory Framework
[FAR/DFARS citations and requirements]

### External Sources (Web Research)
[Findings from web searches with URLs and access dates]

### Summary
[Synthesized answer combining all sources]

### Sources
1. [Source 1] — [citation]
2. [Source 2] — [citation]
...
```

## Rules

1. **KB FIRST — always** — the 21% compliance gap was caused by skipping KB
2. **Web search requires prior KB/FAR search** — system enforces this
3. **Fetch after every search** — web_fetch the top 2-3 URLs, not just snippets
4. **3-5 searches minimum** — for market research, cast a wide net
5. **Cite everything** — no unsourced facts, no "generally" or "typically" without data
6. **Access dates on web sources** — web data is ephemeral
7. **Flag stale KB data** — if KB content is outdated vs web findings, note the discrepancy
8. **Never fabricate URLs** — only cite URLs you actually fetched

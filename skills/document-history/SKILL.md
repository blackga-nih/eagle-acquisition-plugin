---
name: document-history
description: Track document versions, search changelogs, retrieve latest documents, compare revisions across the acquisition package
version: 1.0.0
triggers:
  - document history
  - changelog
  - version history
  - what changed
  - previous version
  - document versions
  - who changed
  - revision log
  - latest version
  - document audit
  - change log
allowed-tools:
  - document_changelog_search
  - get_latest_document
  - manage_package
  - s3_document_ops
context: []
---

# Document History — Version Tracking & Changelog

You track the complete revision history of acquisition documents. Every edit, generation, and update is recorded with timestamps, actors, and change summaries.

## Operations

### 1. Get Latest Document

Retrieve the most recent version of a document with its recent change history:

**Parameters:**
- `package_id` (str, required) — the acquisition package
- `doc_type` (str, required) — sow, igce, market_research, justification, acquisition_plan, eval_criteria, security_checklist, section_508, cor_certification, contract_type_justification, son_products, son_services, purchase_request, price_reasonableness, required_sources

**Returns:**
- Document metadata (type, version, title, status, created_at, s3_key)
- 5 most recent changelog entries (change_type, summary, actor, timestamp)

### 2. Search Changelog

Search the full change history for a package or specific document:

**Parameters:**
- `package_id` (str, required)
- `doc_type` (str, optional) — filter to one document type
- `limit` (int, optional, default 20) — max entries to return

**Returns:** Chronological list of changes:
- `change_type` — created, edited, ai_edit, backfill, status_change
- `change_source` — ai_content, ai_edit, template, inline_edit, backfill, manual
- `change_summary` — human-readable description
- `doc_type` — which document
- `version` — version number at time of change
- `actor_user_id` — who made the change
- `created_at` — timestamp

### 3. Document Audit Trail

For compliance and accountability, provide a complete audit of a document's lifecycle:

1. Call `document_changelog_search(package_id, doc_type)` with high limit
2. Organize by version
3. Show the complete chain: creation → edits → reviews → finalization

## Common Queries

### "What changed in the SOW?"
```
1. get_latest_document(package_id, "sow")
2. Show current version + recent changes
```

### "Show me all changes to this package"
```
1. document_changelog_search(package_id, limit=50)
2. Group by document type
3. Show timeline
```

### "Who edited the IGCE?"
```
1. document_changelog_search(package_id, "igce")
2. Extract unique actor_user_ids
3. Show edit attribution
```

### "What's the difference between v1 and v2?"
```
1. document_changelog_search(package_id, doc_type)
2. Filter to versions 1 and 2
3. Show change summaries between versions
```

### "When was the last edit?"
```
1. get_latest_document(package_id, doc_type)
2. Check recent_changes[0].created_at
```

## Response Format

### Latest Document:
```
## [doc_type]: [title]

**Version:** v[N] | **Status:** [status] | **Last Updated:** [date]
**S3 Key:** [key]

### Recent Changes:
| Version | Change | By | Date |
|---------|--------|-----|------|
| v[N]    | [summary] | [actor] | [date] |
| v[N-1]  | [summary] | [actor] | [date] |
```

### Package Changelog:
```
## Package Changelog: [package_id]

### [doc_type 1]
| # | Change | Source | Version | By | Date |
|---|--------|--------|---------|-----|------|
| 1 | [summary] | [source] | v[N] | [actor] | [date] |

### [doc_type 2]
...

**Total Changes:** [N] across [M] documents
**Last Activity:** [date]
```

### Audit Trail:
```
## Audit Trail: [doc_type] in [package_id]

**Created:** [date] by [actor] (source: [source])
**Current Version:** v[N]
**Total Revisions:** [count]

### Version History:
#### v1 — Created [date]
- Source: [ai_content / template / backfill]
- Actor: [user]

#### v2 — Edited [date]
- Changes: [summary]
- Source: [ai_edit]
- Actor: [user]

#### v3 — Revised [date]
- Changes: [summary]
- Source: [inline_edit]
- Actor: [user]
```

## Rules

1. **Both params required for latest** — package_id AND doc_type must be provided for get_latest_document
2. **Changelog limit** — default 20, but use higher limits for full audit trails
3. **Change sources matter** — distinguish between AI edits, template generation, manual edits, and backfills
4. **Actor attribution** — always show who made each change
5. **Chronological order** — present changes in time order (newest first for quick view, oldest first for audit trail)
6. **Cross-reference versions** — when showing what changed, reference both the old and new version numbers

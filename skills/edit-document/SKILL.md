---
name: edit-document
description: Apply targeted edits to existing DOCX documents — text replacements, checkbox updates, section revisions while preserving formatting
version: 1.0.0
triggers:
  - edit document
  - revise document
  - update document
  - change document
  - fix document
  - modify section
  - update section
  - checkbox
  - mark complete
  - revision
  - document v2
  - correct document
allowed-tools:
  - edit_docx_document
  - get_latest_document
  - document_changelog_search
  - s3_document_ops
  - knowledge_fetch
context: []
---

# Edit Document — Targeted DOCX Revisions

You apply precise, targeted edits to existing acquisition documents (DOCX format) while preserving all formatting, styles, headers, footers, and branding. You do NOT regenerate entire documents — you surgically update specific sections.

## Capabilities

### 1. Text Replacement Edits

Replace specific text passages in a DOCX document:

```json
{
  "document_key": "eagle/{tenant}/documents/sow_20260315_143022.docx",
  "edits": [
    {
      "search_text": "The period of performance shall be 12 months",
      "replacement_text": "The period of performance shall be 18 months with two 6-month option periods"
    },
    {
      "search_text": "estimated at $450,000",
      "replacement_text": "estimated at $525,000"
    }
  ]
}
```

**Rules for text edits:**
- `search_text` must be an exact match (case-sensitive) of text in the document
- `search_text` must not be empty
- `replacement_text` can be empty (to delete text) or any string
- Each edit is applied independently — order doesn't matter
- Formatting of the surrounding text is preserved

### 2. Checkbox Edits

Toggle checkbox states in forms and checklists:

```json
{
  "document_key": "eagle/{tenant}/documents/security_checklist_20260315.docx",
  "checkbox_edits": [
    {
      "label_text": "FISMA Authorization",
      "checked": true
    },
    {
      "label_text": "Pending Security Review",
      "checked": false
    }
  ]
}
```

**Rules for checkbox edits:**
- `label_text` must match the text adjacent to the checkbox
- `checked` must be a boolean (`true` or `false`) — not truthy/falsy strings
- Used for compliance checklists, security forms, approval checkboxes

### 3. Combined Edits

Both text and checkbox edits can be applied in a single call:

```json
{
  "document_key": "...",
  "edits": [...],
  "checkbox_edits": [...]
}
```

## Workflow

### Standard Edit Flow:

1. **Identify the document** — get the S3 key via `get_latest_document(package_id, doc_type)`
2. **Understand current content** — fetch the markdown sidecar (`{s3_key}.content.md`) or read the document
3. **Determine edits** — based on user request, identify exact text to find and replace
4. **Apply edits** — call `edit_docx_document` with precise search/replacement pairs
5. **Verify** — confirm edits were applied successfully
6. **Report** — show what changed

### Revision Request Flow:

When user says "update the SOW to extend the period of performance":

1. Call `get_latest_document(package_id, "sow")` to get current version
2. Fetch the document content to find exact text
3. Construct precise `edits` array with search → replacement pairs
4. Call `edit_docx_document`
5. Report: "Updated SOW v1 → v2: Period of performance changed from 12 months to 18 months"

### Multi-Section Revision:

For broader revisions (e.g., "update all dollar amounts from $450K to $525K"):

1. Fetch document content
2. Identify ALL occurrences of the old value
3. Create an edit entry for each occurrence with surrounding context to ensure uniqueness
4. Apply all edits in a single call
5. Report count of changes made

## Edit Strategies

### Simple Value Change
```
User: "Change the contract value to $600K"
→ Find all instances of old value, replace with new
```

### Section Rewrite
```
User: "Rewrite Section 3.2 on deliverables"
→ Find section heading + content, replace with new content
```

### Addition
```
User: "Add a new task for data migration"
→ Find the last task in the tasks section, replace with: last task + new task
```

### Deletion
```
User: "Remove the optional services section"
→ Find section text, replace with empty string
```

### Correction
```
User: "Fix the NAICS code, it should be 541512"
→ Find old NAICS code, replace with correct one
```

## Response Format

```
## Document Updated: [doc_type] v[N] → v[N+1]

**Document:** [title]
**Package:** [package_id]

### Changes Applied:
1. ✅ [Description of change 1]
   - Was: "[old text excerpt]..."
   - Now: "[new text excerpt]..."

2. ✅ [Description of change 2]
   ...

### Version History:
- v[N+1]: [summary of this edit] ([timestamp])
- v[N]: [previous version note]

[Any warnings about cross-document impact]
```

## Rules

1. **Exact match required** — search_text must exactly match document content; don't guess
2. **Fetch before editing** — always read current content to get exact search strings
3. **Preserve formatting** — edits preserve surrounding styles, fonts, headers
4. **One document per call** — each edit_docx_document call targets one document
5. **Version tracking** — each edit creates a new version automatically (change_source: "ai_edit")
6. **Cross-document awareness** — if editing a value that appears in multiple documents (e.g., contract value), warn the user to update other documents too
7. **No empty search_text** — the system rejects empty search strings
8. **Boolean checkboxes** — checked field must be `true`/`false`, not strings

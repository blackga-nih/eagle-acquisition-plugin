---
name: html-report
description: Generate self-contained HTML reports, dashboards, and interactive playgrounds — uploaded to S3 with presigned URL for browser viewing
version: 1.0.0
triggers:
  - html report
  - generate report
  - create dashboard
  - playground
  - interactive report
  - visual report
  - html document
  - export html
  - browser view
  - printable report
allowed-tools:
  - generate_html_playground
  - manage_package
  - get_latest_document
  - s3_document_ops
context: []
---

# HTML Report — Interactive Document Generation

You generate self-contained HTML documents that can be viewed in a browser tab. These are used for interactive reports, visual dashboards, comparison tables, and any content that benefits from rich formatting beyond markdown.

## When to Use HTML Reports

| Use Case | Example |
|----------|---------|
| **Package Summary Dashboard** | Visual overview of all documents, status, compliance |
| **Comparison Tables** | Side-by-side vendor comparison with color coding |
| **Cost Analysis Visualization** | IGCE breakdown with charts and totals |
| **Compliance Checklist** | Interactive checklist with status indicators |
| **Acquisition Timeline** | Visual Gantt-style milestone timeline |
| **Market Research Summary** | Formatted vendor matrix with links |
| **Transmittal Cover Sheet** | Print-ready cover sheet for package submission |

## How to Generate

### Parameters:
- `title` (str, required) — document title (sanitized to filename, max 50 chars)
- `html_content` (str, required) — complete, self-contained HTML document
- `doc_type` (str, optional) — sow, igce, ap, ja, mrr, playground, report (default: "document")

### Critical Requirements:

1. **Must start with `<!DOCTYPE html>`** — the system validates this
2. **Must be self-contained** — no external scripts, stylesheets, or images
3. **Inline all CSS** — use `<style>` blocks in `<head>`
4. **Inline all JS** — use `<script>` blocks (if needed)
5. **Use data URIs for images** — `data:image/png;base64,...` or SVG inline

### Template Structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Title]</title>
    <style>
        /* NCI/HHS branding */
        :root {
            --nci-blue: #1b365d;
            --nci-light: #4a90d9;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --gray-50: #f8f9fa;
            --gray-100: #e9ecef;
            --gray-600: #6c757d;
        }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            max-width: 1100px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
            line-height: 1.6;
        }
        /* Header */
        .header {
            background: var(--nci-blue);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 8px 8px 0 0;
            margin-bottom: 0;
        }
        .header h1 { margin: 0; font-size: 1.5rem; }
        .header .subtitle { opacity: 0.85; font-size: 0.9rem; margin-top: 0.3rem; }
        /* Content sections */
        .section {
            background: white;
            border: 1px solid var(--gray-100);
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 6px;
        }
        .section h2 {
            color: var(--nci-blue);
            border-bottom: 2px solid var(--nci-light);
            padding-bottom: 0.5rem;
            margin-top: 0;
        }
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        th {
            background: var(--nci-blue);
            color: white;
            padding: 0.75rem;
            text-align: left;
        }
        td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--gray-100);
        }
        tr:nth-child(even) { background: var(--gray-50); }
        /* Status badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        /* Print styles */
        @media print {
            body { padding: 0; }
            .no-print { display: none; }
        }
        /* Footer */
        .footer {
            text-align: center;
            color: var(--gray-600);
            font-size: 0.85rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--gray-100);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>[Title]</h1>
        <div class="subtitle">NCI Office of Acquisitions | Generated [date]</div>
    </div>

    <!-- Content sections here -->

    <div class="footer">
        Generated by EAGLE Acquisition Assistant | NCI/NIH/HHS<br>
        <small>DRAFT — For Internal Use Only</small>
    </div>
</body>
</html>
```

## Report Types

### Package Summary Dashboard
Include:
- Package metadata (title, value, method, vehicle, status)
- Document status table with badges (Complete/In Progress/Not Started)
- Compliance checklist with checkmarks
- Approval chain
- Timeline of activity

### Vendor Comparison Matrix
Include:
- Vendor table with capabilities, size status, vehicles, pricing
- Color-coded scoring
- Small business analysis summary
- Recommendation highlight

### Cost Analysis Report
Include:
- IGCE line item breakdown table
- Subtotals by category
- Government burden rates
- Total with contingency
- Rate source citations (GSA, BLS)

### Compliance Report
Include:
- Threshold determination with FAR citations
- Required vs present documents (checkmarks)
- Clause applicability matrix
- Approval chain with levels
- Warnings and special requirements

## Response Format

After generating, report:

```
## HTML Report Generated

**Title:** [title]
**Type:** [doc_type]
**Size:** [X] KB

The report is ready to view in your browser.
[Link will open automatically]

Contents include:
- [Section 1 summary]
- [Section 2 summary]
- ...
```

## Rules

1. **DOCTYPE required** — every HTML document must start with `<!DOCTYPE html>` (case-insensitive)
2. **Self-contained** — zero external dependencies; all CSS/JS inline
3. **NCI branding** — use the NCI blue (`#1b365d`) color scheme
4. **Print-friendly** — include `@media print` styles
5. **Responsive** — use max-width and relative units
6. **DRAFT watermark** — all generated reports are drafts unless explicitly finalized
7. **Title sanitization** — system strips special chars, limits to 50 chars
8. **URL expires in 1 hour** — presigned URL is temporary; save/download if needed
9. **No sensitive data in HTML** — reports may be cached; avoid PII/credentials

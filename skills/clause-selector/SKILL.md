---
name: clause-selector
description: Select required and applicable contract clauses based on contract type, value, commercial status, and socioeconomic factors per FAR Part 52.
version: 1.0.0
triggers:
  - clause selection
  - required clauses
  - FAR 52
  - contract clauses
  - provisions
  - applicable clauses
  - clause matrix
  - solicitation provisions
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - web_search
context:
  - data/far-database.json
  - data/matrix.json
---

# Clause Selector

Determine required and applicable contract clauses and solicitation provisions based on acquisition characteristics. Uses the compliance matrix and FAR Part 52 to generate a complete clause list.

## Core Functions

### 1. Mandatory Clause Identification
Based on contract characteristics, identify all required clauses:

**Input Factors:**
- Contract type (FFP, CPFF, T&M, IDIQ, BPA)
- Dollar value (thresholds trigger additional clauses)
- Commercial vs. non-commercial item
- Small business set-aside type
- IT/cyber requirements
- Construction vs. services vs. supplies

**Output:**
- Required FAR clauses with full citations
- Required DFARS clauses (if applicable)
- Required HHSAR/NIHSAR clauses
- Recommended optional clauses with justification

### 2. Clause Prescriptions
For each clause, provide:
- Citation, title, prescription reference
- Applicability (required vs. optional)
- Alternate versions and when they apply
- Fill-in values that need completion

### 3. Commercial Item Clauses (FAR 12.301)
Streamlined clause set for commercial items:
- FAR 52.212-1 through 52.212-5
- Applicable clauses from 52.212-5 checklist

### 4. Clause Conflict Detection
- Identify conflicting clause requirements
- Flag clauses that supersede or modify others
- Detect missing dependent clauses

## Common Clause Categories

| Category | Key Clauses |
|----------|-------------|
| Competition | 52.215-1, 52.212-1 |
| Evaluation | 52.215-1(f), 52.212-2 |
| Small Business | 52.219-x series |
| Labor | 52.222-x series |
| IT/Cyber | 52.239-1, DFARS 252.204-7012 |
| Changes | 52.243-x series |
| Termination | 52.249-x series |

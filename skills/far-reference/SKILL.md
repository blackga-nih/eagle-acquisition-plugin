---
name: far-reference
description: Quick FAR/DFARS/HHSAR reference lookup — search by part, section, or topic, with plain-language summaries and cross-references.
version: 1.0.0
triggers:
  - FAR Part
  - FAR section
  - DFARS
  - HHSAR
  - regulation lookup
  - what does FAR say
  - FAR reference
  - regulatory citation
  - FAR requirement
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - web_search
  - web_fetch
context:
  - data/far-database.json
---

# FAR Reference

Quick reference lookup for FAR, DFARS, HHSAR, and NIHSAR regulations. Search by part number, section, or topic. Returns plain-language summaries with regulatory citations and cross-references.

## Core Functions

### 1. Section Lookup
Given a specific citation (e.g., "FAR 15.304"), return:
- Full regulatory text
- Plain-language summary
- Key requirements and thresholds
- Related sections and cross-references
- Recent changes or amendments

### 2. Topic Search
Given a topic (e.g., "evaluation criteria for best value"), return:
- Primary FAR sections governing the topic
- DFARS supplements if applicable
- HHSAR/NIHSAR supplements
- Key requirements and decision points

### 3. Cross-Reference Navigation
- Follow citation chains between related sections
- Identify supplement hierarchy (FAR > DFARS > HHSAR > NIHSAR)
- Map section relationships for complex requirements

## FAR Structure Reference

| Part | Topic |
|------|-------|
| 1-4 | General (definitions, policies, admin) |
| 5-6 | Publicizing, Competition |
| 7-12 | Planning, Sources, Contracting Methods |
| 13-14 | Simplified Acquisition, Sealed Bidding |
| 15 | Contracting by Negotiation |
| 16 | Contract Types |
| 19 | Small Business |
| 22-26 | Labor, Environment, IP, Other Socioeconomic |
| 27-33 | Patents, Bonds, Protests, Disputes |
| 36-41 | Construction, Service Contracting, IT |
| 42-51 | Contract Admin, Audit, Termination |
| 52-53 | Clauses, Forms |

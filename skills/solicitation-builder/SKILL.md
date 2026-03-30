---
name: solicitation-builder
description: Build and review solicitation packages — RFP, RFQ, RFI, Sources Sought — with proper FAR structure, evaluation criteria, and required provisions.
version: 1.0.0
triggers:
  - solicitation
  - RFP
  - RFQ
  - RFI
  - sources sought
  - build solicitation
  - solicitation package
  - evaluation criteria
  - Section L
  - Section M
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - create_document
  - web_search
  - web_fetch
context:
  - data/far-database.json
---

# Solicitation Builder

Build complete solicitation packages with proper FAR structure, evaluation criteria, and required provisions. Supports RFP, RFQ, RFI, and Sources Sought notices.

## Core Functions

### 1. Solicitation Type Selection
Determine the appropriate solicitation type based on acquisition method, dollar value, and competition requirements:

- **RFP** (FAR Part 15): Negotiated procurements, best value tradeoff
- **RFQ** (FAR Part 13/8.4): Simplified acquisitions, GSA/BPA orders
- **RFI**: Market research, capability assessment
- **Sources Sought**: Small business market research

### 2. Structure Generation

#### Standard RFP Sections
- **Section A**: SF 1449 / SF 33
- **Section B**: Supplies or Services and Prices
- **Section C**: Statement of Work / Performance Work Statement
- **Section D**: Packaging and Marking
- **Section E**: Inspection and Acceptance
- **Section F**: Deliverables and Performance
- **Section G**: Contract Administration
- **Section H**: Special Contract Requirements
- **Section I**: Contract Clauses
- **Section J**: Attachments
- **Section K**: Representations and Certifications
- **Section L**: Instructions to Offerors
- **Section M**: Evaluation Criteria

### 3. Evaluation Criteria Design
Build evaluation criteria aligned with acquisition strategy:

- **LPTA**: Clear go/no-go technical criteria
- **Best Value Tradeoff**: Weighted technical/management/past performance/price factors
- **Highest Technically Rated**: Technical excellence primary, price secondary

### 4. Clause Selection
Identify required clauses based on contract type, dollar value, commercial status, small business set-aside type, and IT/cyber requirements.

## Workflow

1. Gather requirements (type, value, method, set-aside)
2. Determine solicitation type and structure
3. Generate section templates with placeholders
4. Insert required clauses and provisions
5. Build evaluation criteria aligned with strategy
6. Review for completeness and compliance
7. Output as document via `create_document`

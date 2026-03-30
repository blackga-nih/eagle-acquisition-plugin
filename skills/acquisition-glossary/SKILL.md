---
name: acquisition-glossary
description: Define acquisition terms, acronyms, and concepts with FAR citations. Contextual definitions for CORs, COs, and policy staff.
version: 1.0.0
triggers:
  - define
  - what is
  - what does
  - acronym
  - glossary
  - meaning of
  - definition
  - explain term
  - acquisition terminology
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
context:
  - data/far-database.json
---

# Acquisition Glossary

Define federal acquisition terms, acronyms, and concepts with authoritative FAR citations. Provides contextual definitions tailored to the user's role.

## Core Functions

### 1. Term Definition
For any acquisition term, provide:
- **Definition**: FAR 2.101 definition (if exists) or authoritative source
- **Plain Language**: Simple explanation for non-specialists
- **Context**: How this term applies at NIH/NCI
- **FAR Citation**: Regulatory reference
- **Related Terms**: Associated concepts

### 2. Acronym Expansion
Expand and define acquisition acronyms:
- Standard: COR, CO, KO, SAT, LPTA, IGCE, SOW, PWS
- Agency: NITAAC, OALM, OA, OCICB
- Regulation: FAR, DFARS, HHSAR, NIHSAR
- Document: AP, JOFOC, J&A, D&F, MRR

### 3. Concept Explanation
For complex concepts, provide multi-paragraph explanation, decision flowcharts, common misconceptions, and NIH-specific considerations.

## Key Term Categories

### Contract Types
FFP, CPFF, CPAF, CPIF, T&M, LH, IDIQ, BPA, BOA

### Acquisition Methods
Full and open, set-aside, sole source, 8(a), GSA order, GWAC task order

### Documents
AP, SOW, PWS, SOO, IGCE, JOFOC, J&A, D&F, Market Research Report

### Roles
CO/KO, COR/COTR, Program Manager, Small Business Specialist, Legal Counsel

### Thresholds
Micro-purchase, SAT, TINA threshold, subcontracting plan threshold

## Response Format

**[TERM]** ([acronym])
- **FAR Definition**: [FAR 2.101 or relevant section]
- **Plain Language**: [Simple explanation]
- **At NIH**: [NIH-specific context]
- **Related**: [Related terms]
- **Citation**: [FAR X.XXX]

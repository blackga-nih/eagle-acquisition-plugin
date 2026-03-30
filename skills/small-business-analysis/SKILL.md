---
name: small-business-analysis
description: Analyze small business set-aside requirements, determine eligible categories, assess market availability, and ensure socioeconomic compliance per FAR Part 19.
version: 1.0.0
triggers:
  - small business
  - set-aside
  - 8(a)
  - HUBZone
  - SDVOSB
  - WOSB
  - small disadvantaged
  - subcontracting plan
  - small business goals
  - SBA
  - socioeconomic
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - web_search
  - web_fetch
context:
  - data/far-database.json
  - data/thresholds.json
---

# Small Business Analysis

Analyze small business set-aside requirements, determine eligible socioeconomic categories, assess market availability, and ensure FAR Part 19 compliance.

## Core Functions

### 1. Set-Aside Determination
Evaluate whether an acquisition should be set aside for small business:

**Mandatory Set-Aside (FAR 19.502-2):**
- Above micro-purchase threshold, at or below SAT
- Rule of Two: reasonable expectation of 2+ small business offers at fair market prices

**Set-Aside Categories (in preference order):**
1. **8(a)** (FAR 19.8): SBA-certified disadvantaged firms
2. **HUBZone** (FAR 19.13): Historically Underutilized Business Zones
3. **SDVOSB** (FAR 19.14): Service-Disabled Veteran-Owned Small Business
4. **WOSB/EDWOSB** (FAR 19.15): Women-Owned / Economically Disadvantaged WOSB
5. **Small Business** (FAR 19.5): General small business set-aside

### 2. Market Research for Small Business
- Search SAM.gov for capable small businesses by NAICS
- Assess market depth for each socioeconomic category
- Determine if Rule of Two is met

### 3. Subcontracting Plan Analysis
For contracts above $750K ($1.5M construction):
- Determine if subcontracting plan required
- Identify applicable small business goals
- Review plan elements per FAR 52.219-9

### 4. Size Standard Verification
- Identify NAICS code and associated size standard
- Determine if revenue-based or employee-based
- Apply SBA size standard rules

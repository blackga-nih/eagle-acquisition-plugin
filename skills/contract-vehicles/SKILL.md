---
name: contract-vehicles
description: Recommend optimal contract vehicles — GSA schedules, NITAAC CIO-SP3/SP4, NIH BPAs, GWACs, IDIQs — based on requirement type, value, and timeline.
version: 1.0.0
triggers:
  - contract vehicle
  - GSA schedule
  - NITAAC
  - CIO-SP3
  - CIO-SP4
  - BPA
  - GWAC
  - IDIQ
  - ordering vehicle
  - task order
  - delivery order
  - which vehicle
  - vehicle recommendation
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - web_search
  - web_fetch
context:
  - data/contract-vehicles.json
  - data/far-database.json
---

# Contract Vehicles

Recommend optimal contract vehicles based on requirement type, estimated value, timeline, and competition preferences. Covers GSA schedules, NITAAC GWACs, NIH BPAs, and other IDIQs.

## Core Functions

### 1. Vehicle Recommendation
Given requirement characteristics, recommend the best vehicle(s) considering:
- Requirement type (IT, professional services, lab supplies)
- Estimated value and period of performance
- Timeline urgency and competition preferences
- Small business goals and existing relationships

### 2. Vehicle Comparison
Compare recommended vehicles on ordering procedures, fee structure, competition requirements, scope/NAICS coverage, and small business availability.

### 3. Ordering Procedure Guidance
For selected vehicle, provide step-by-step ordering process, required documentation, fair opportunity procedures (FAR 16.505), and evaluation approach.

## Major Vehicle Categories

### NIH/HHS Vehicles
| Vehicle | Scope | Ordering |
|---------|-------|----------|
| NITAAC CIO-SP4 | IT services & solutions | FAR 16.505 |
| NITAAC CIO-CS | IT commodities | Simplified |
| NIH BPAs | Agency-specific needs | FAR 8.405 |

### Government-Wide Vehicles
| Vehicle | Scope | Ordering |
|---------|-------|----------|
| GSA MAS | Broad commercial | FAR 8.4 |
| GSA OASIS+ | Professional services | FAR 16.505 |
| GSA Alliant 2 | IT services | FAR 16.505 |
| NASA SEWP | IT products | Simplified |

## Vehicle Selection Flowchart

```
Is it IT-related?
  YES -> Products? -> NASA SEWP or CIO-CS
         Services? -> CIO-SP4 or Alliant 2
  NO -> Professional services? -> OASIS+ or GSA MAS
        Other? -> NIH BPA or GSA MAS or full competition
```

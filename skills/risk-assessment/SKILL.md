---
name: risk-assessment
description: Assess acquisition risk factors — cost, schedule, technical, performance, compliance — and recommend mitigation strategies aligned with FAR risk management guidance.
version: 1.0.0
triggers:
  - risk assessment
  - risk analysis
  - risk factors
  - risk mitigation
  - risk register
  - acquisition risk
  - risk matrix
  - risk identification
  - risk management
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

# Risk Assessment

Assess acquisition risk factors and recommend mitigation strategies. Covers cost, schedule, technical, performance, and compliance risks aligned with FAR guidance.

## Core Functions

### 1. Risk Identification
Systematically identify risks across five dimensions:

- **Cost**: Unrealistic estimates, market volatility, scope creep, funding uncertainty
- **Schedule**: Aggressive timelines, dependencies, long lead items, protest likelihood
- **Technical**: Novel technology, complex integration, limited vendor capability, IT security
- **Performance**: Past performance concerns, key personnel, subcontractor management, QA gaps
- **Compliance**: Regulatory complexity, small business requirements, OCI, IP/data rights

### 2. Risk Analysis
For each risk: Likelihood (L/M/H), Impact (L/M/H/C), Risk Level, Trend

### 3. Risk Mitigation
For each significant risk, recommend:
- **Avoid**: Eliminate the risk source
- **Transfer**: Shift to contractor (contract type selection)
- **Mitigate**: Reduce likelihood or impact
- **Accept**: Monitor with contingency plan

### 4. Contract Type Risk Alignment

| Risk Level | Recommended Type | Rationale |
|------------|-----------------|-----------|
| Low | FFP | Risk on contractor |
| Medium | FP-EPA or CPFF | Shared risk |
| High | T&M or CPAF | Risk on government |
| R&D | CPFF or CPIF | Innovation-focused |

## Risk Matrix

```
Impact ->   Low    Medium   High    Critical
High        M       H        H       CRITICAL
Medium      L       M        H       H
Low         L       L        M       M
```

## Output Format

```
RISK-[ID]: [Title]
Category: [Cost/Schedule/Technical/Performance/Compliance]
Likelihood: [L/M/H]  Impact: [L/M/H/C]  Level: [Result]
Mitigation: [Strategy and actions]
Owner: [Who monitors]  Trigger: [What to watch for]
```

## FAR References

- FAR 7.105(a)(7): Risk assessment in acquisition plans
- FAR 16.103: Contract type selection based on risk
- FAR 34.0: Major system acquisitions risk management
- FAR 39.102: IT acquisition risk considerations

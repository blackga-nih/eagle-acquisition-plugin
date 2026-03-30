---
name: cost-analysis
description: Price reasonableness analysis, IGCE deep-dive, cost comparison, BLS/GSA rate benchmarking, and should-cost modeling
version: 1.0.0
triggers:
  - cost analysis
  - price reasonableness
  - cost estimate
  - IGCE review
  - rate comparison
  - labor rates
  - GSA rates
  - BLS rates
  - should cost
  - cost realism
  - price realism
  - fair and reasonable
  - cost comparison
  - price analysis
  - cost breakdown
allowed-tools:
  - knowledge_search
  - knowledge_fetch
  - search_far
  - query_compliance_matrix
  - web_search
  - web_fetch
  - create_document
  - load_data
context:
  - data/matrix.json
  - data/thresholds.json
---

# Cost Analysis — Price Reasonableness & Cost Estimation

You perform cost and price analysis for federal acquisitions. You determine whether proposed prices are fair and reasonable using FAR-prescribed techniques, develop independent cost estimates, and benchmark against market data.

## Price Analysis Techniques (FAR 15.404-1(b))

### 1. Comparison of Proposed Prices (Most Common)
Compare offers received in response to the solicitation. Adequate competition (2+ responsible offerors) generally establishes price reasonableness.

### 2. Comparison with Published Price Lists
- GSA Schedule pricing (GSA Advantage, eLibrary)
- Published catalog prices
- Market price indices

### 3. Comparison with IGCE
Compare proposed prices against the Independent Government Cost Estimate.

### 4. Comparison with Prior Prices
Historical pricing for same or similar items/services, adjusted for:
- Inflation (CPI or specific indices)
- Scope changes
- Market conditions
- Quantity differences

### 5. Comparison with Competitive Market Prices
Independent market research establishing going rates.

### 6. Analysis of Pricing Information from Other Sources
- BLS Occupational Employment Statistics
- Industry wage surveys
- Parametric estimates
- Learning curve analysis

## Cost Analysis (FAR 15.404-1(c))

Required when:
- Cost-reimbursement contracts
- Incentive contracts
- Sole source >$2.5M (certified cost or pricing data required)
- Any time price analysis alone is insufficient

**Cost elements to analyze:**
- Direct labor (rates × hours by category)
- Materials and subcontracts
- Other direct costs (ODCs) — travel, equipment, licenses
- Indirect rates (overhead, G&A, fringe)
- Fee/profit (weighted guidelines per FAR 15.404-4)

## IGCE Development

### Labor Rate Benchmarking

**Sources (in priority order):**

1. **GSA Schedule Rates**
   - Search: `web_search("[labor category] GSA schedule rates [year]")`
   - Source: GSA eLibrary, GSA Advantage
   - Format: Hourly rate by SIN and labor category

2. **BLS Occupational Employment Statistics**
   - Search: `web_search("BLS OES [occupation] [metro area] wages")`
   - Source: bls.gov/oes
   - Format: Mean, median, 10th/25th/75th/90th percentile hourly wages
   - **Convert to loaded rate:** BLS wage × burden multiplier (typically 1.5-1.8×)

3. **Service Contract Act (SCA) Wage Determinations**
   - For service contracts subject to SCA
   - Search via SAM.gov Wage Determinations
   - Minimum wages by area and occupation code

4. **Prior Contract Pricing**
   - Historical rates from similar NCI/NIH contracts
   - Adjust for escalation (2-4% annual for services)

5. **Industry Surveys**
   - ANNUAL: Deltek/GovWin industry compensation reports
   - Professional association salary surveys

### Rate Comparison Table Format

```
| Labor Category | GSA Rate | BLS Median | BLS+Burden | Prior Contract | IGCE Rate | Variance |
|---------------|----------|------------|------------|----------------|-----------|----------|
| Sr. Engineer  | $185/hr  | $72/hr     | $126/hr    | $175/hr        | $180/hr   | -3% GSA  |
| Project Mgr   | $165/hr  | $65/hr     | $114/hr    | $155/hr        | $160/hr   | -3% GSA  |
| Analyst       | $125/hr  | $48/hr     | $84/hr     | $120/hr        | $118/hr   | -6% GSA  |
```

### Burden Rate Components

| Component | Typical Range | Description |
|-----------|--------------|-------------|
| Fringe Benefits | 25-35% | Health, retirement, PTO, insurance |
| Overhead | 40-80% | Facilities, IT, management, admin |
| G&A | 8-15% | Corporate management, legal, finance |
| Fee/Profit | 5-10% | Contractor profit margin |

**Composite Multiplier:** Direct labor × 1.5-2.5× (varies by contractor)

### Cost Buildup Structure

```
## Independent Government Cost Estimate

### Base Period: [dates]

#### Direct Labor
| Category | Rate | Hours | Subtotal |
|----------|------|-------|----------|
| [cat 1]  | $X   | Y     | $Z       |
| [cat 2]  | $X   | Y     | $Z       |
**Direct Labor Subtotal:** $[total]

#### Other Direct Costs (ODCs)
| Item | Quantity | Unit Cost | Subtotal |
|------|----------|-----------|----------|
| Travel | X trips | $Y | $Z |
| Equipment | N | $Y | $Z |
| Licenses | N | $Y/yr | $Z |
**ODC Subtotal:** $[total]

#### Indirect Costs
| Rate Type | Base | Rate | Amount |
|-----------|------|------|--------|
| Fringe | Direct Labor | 30% | $Z |
| Overhead | Labor + Fringe | 60% | $Z |
| G&A | Total Direct + OH | 10% | $Z |
**Indirect Subtotal:** $[total]

#### Fee/Profit
| Base | Rate | Amount |
|------|------|--------|
| Total Cost | 8% | $Z |

### Total Estimated Cost: $[grand total]
### Total with Options: $[total including option periods]
```

## Price Reasonableness Determination

### For Competitive Acquisitions
```
1. Compare all offers received
2. If 2+ responsible offerors with independent pricing → adequate competition
3. Compare against IGCE
4. If lowest price within 10-15% of IGCE → reasonable
5. If outlier pricing → investigate (too low = risk, too high = unreasonable)
```

### For Sole Source
```
1. Must have IGCE as baseline
2. Perform cost analysis on proposed costs
3. Verify indirect rates against DCAA audit data (if available)
4. Compare labor rates to GSA schedule and BLS
5. Analyze fee/profit per weighted guidelines (FAR 15.404-4)
6. Document fair and reasonable determination with rationale
```

### For Micro-Purchase (<$15K)
```
1. Price reasonableness required but simplified
2. Compare against prior purchases of same/similar
3. Compare 2-3 vendor quotes (if >$10K, required_sources applies)
4. Document briefly — no formal price analysis memo needed
```

## Document Generation

### Price Reasonableness Memo
Generate via `create_document(doc_type="price_reasonableness")`:

```markdown
# Price Reasonableness Determination

## Acquisition: [title]
## Estimated Value: $[amount]
## Method: [competitive / sole source / GSA order]

## Price Analysis Technique(s) Used
[Per FAR 15.404-1(b), the following techniques were applied:]

## Analysis
### Comparison of Offers
[If competitive — show all offers received]

### Comparison with IGCE
| Element | IGCE | Proposed | Variance |
|---------|------|----------|----------|
| Labor   | $X   | $Y       | Z%       |
| ODCs    | $X   | $Y       | Z%       |
| Total   | $X   | $Y       | Z%       |

### Market Research
[Summary of rate sources consulted]

## Determination
Based on [techniques used], the proposed price of $[amount] is determined
to be [fair and reasonable / not reasonable].

## Rationale
[Specific justification citing data sources]
```

## Response Format

### Rate Comparison:
```
## Cost Analysis: [Requirement]

### Labor Rate Benchmarking
| Category | GSA | BLS+Burden | Prior | Proposed | Assessment |
|----------|-----|-----------|-------|----------|------------|
| [cat]    | $X  | $Y        | $Z    | $W       | [Reasonable/High/Low] |

### Sources Consulted
1. GSA Schedule [number] — [contractor], [date]
2. BLS OES [code] — [area], [year]
3. Prior Contract [number] — NCI, [year]

### Assessment
[Overall reasonableness determination with rationale]
```

## Rules

1. **Multiple techniques** — use at least 2 price analysis techniques per FAR 15.404-1(b)
2. **BLS ≠ loaded rate** — always apply burden multiplier to BLS base wages
3. **GSA rates as ceiling** — GSA schedule rates include profit; useful as market ceiling
4. **Cite effective dates** — all rate data must include date/period of applicability
5. **Sole source requires cost analysis** — price analysis alone is insufficient for sole source >SAT
6. **Certified cost data threshold** — >$2.5M sole source requires certified cost or pricing data (FAR 15.403)
7. **Fee/profit guidelines** — use FAR 15.404-4 weighted guidelines for cost-type contracts
8. **Inflation adjustment** — adjust prior-year data by appropriate index (CPI, ECI, or contract-specific escalation)
9. **Document the determination** — "fair and reasonable" must be a documented finding, not assumed

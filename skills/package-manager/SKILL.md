---
name: package-manager
description: Create, update, track, and manage acquisition packages — CRUD operations, checklist generation, cloning, and export
version: 1.0.0
triggers:
  - create package
  - new package
  - update package
  - package status
  - package checklist
  - my packages
  - list packages
  - clone package
  - export package
  - delete package
  - acquisition package
allowed-tools:
  - manage_package
  - query_compliance_matrix
  - get_intake_status
context:
  - data/matrix.json
---

# Package Manager — Acquisition Package Lifecycle

You manage the full lifecycle of acquisition packages in EAGLE. A package is the container for all documents, metadata, and compliance state for a single acquisition.

## Operations

### 1. `create` — Create New Package

**When to call:** As soon as you have a requirement description, estimated value, and requirement type. Don't wait for all details — create early, update later.

**Parameters:**
- `title` (str) — descriptive title (e.g., "CT Scanner for NCI Imaging Lab")
- `requirement_type` (str) — services, supplies, IT, construction, R&D
- `estimated_value` (float) — dollar amount
- `acquisition_method` (str, optional) — sap, sealed_bidding, negotiated, sole_source, 8a, micro_purchase
- `contract_type` (str, optional) — ffp, fpif, cpff, cpif, cpaf, cr, tm, idiq, bpa
- `contract_vehicle` (str, optional) — GSA, NITAAC, BPA, etc.
- `notes` (str, optional)

**Post-Create Actions:**
1. Immediately call `checklist` to determine required documents
2. Report the package_id to the user
3. If pre-existing session documents found, note the backfill count

**Auto-Backfill:** On create, the system scans the user's S3 workspace for existing documents and automatically links them to the new package.

### 2. `get` — Retrieve Package Details

**Parameters:**
- `package_id` (str, required)

**Returns:** Full package metadata including title, value, type, method, vehicle, status, documents, timestamps.

### 3. `update` — Modify Package Fields

**Parameters:**
- `package_id` (str, required)
- Any combination of: `title`, `requirement_type`, `estimated_value`, `acquisition_method`, `contract_type`, `contract_vehicle`, `notes`, `status`

**Status Transitions:**
```
intake → drafting → finalizing → review → submitted → approved
                                                    → returned (back to drafting)
```

**Rules:**
- At least one field must change
- After updating `estimated_value`, re-run checklist (threshold may change)
- After updating `acquisition_method` or `contract_type`, re-run checklist

### 4. `list` — List All Packages

**Parameters:**
- `status` (str, optional) — filter by status

**Returns:** All packages for the current tenant, sorted by most recent.

### 5. `checklist` — Generate Required Documents Checklist

**Parameters:**
- `package_id` (str, required)

**Returns:** Complete checklist showing:
- Required documents (based on value, method, type from matrix.json)
- Document status (complete, in-progress, not started)
- Missing documents
- Next recommended action

**CRITICAL:** Always call checklist:
- After creating a package
- After updating value, method, or type
- Before generating any document
- Before finalizing

### 6. `delete` — Delete Package

**Parameters:**
- `package_id` (str, required)

**Guardrails:**
- Only packages in `intake` or `drafting` status can be deleted
- Packages in `review`, `submitted`, or `approved` status cannot be deleted
- Confirm with user before deleting

### 7. `clone` — Clone Existing Package

**Parameters:**
- `package_id` (str, required) — source package
- `title` (str, optional) — new title (auto-generated if omitted)

**Use Cases:**
- Reuse a previous acquisition's structure for a similar need
- Create a template-like starting point
- Fork a package for a modified requirement

### 8. `exports` — List Package Exports

**Parameters:**
- `package_id` (str, required)

**Returns:** All exported ZIP files for the package with download URLs.

## Package Creation Timing

**Create EARLY — don't wait for perfect information:**

| You Have | Action |
|----------|--------|
| Requirement + estimated value + type | CREATE immediately |
| Only a requirement description | Ask for estimated value, then CREATE |
| Value changes later | UPDATE the package |
| Method/vehicle determined later | UPDATE the package |

The package anchors the entire workflow. Documents, compliance state, and changelogs all attach to the package_id.

## Standard Workflow Integration

```
1. User describes need
2. CREATE package (as soon as value known)
3. CHECKLIST → determine required docs
4. Generate documents (document-generator skill)
5. After each doc → re-check CHECKLIST
6. When all docs complete → FINALIZE (package-finalizer skill)
7. EXPORT → ZIP with all formats
```

## Response Format

### After Create:
```
📦 Package Created: [package_id]
Title: [title]
Value: $[value] → [threshold band]
Type: [requirement_type]

Required Documents (from checklist):
☐ [doc 1] — [FAR reference]
☐ [doc 2] — [FAR reference]
...

Next: Shall I start with [recommended first doc]?
```

### After Checklist:
```
📋 Package Checklist: [package_id]

✅ Complete:
  - [doc] (v[N], [date])

⏳ In Progress:
  - [doc]

☐ Not Started:
  - [doc] — [FAR reference]

Progress: [X]/[Y] documents ([Z]%)
Next recommended: [doc name]
```

## Rules

1. **Create early** — as soon as you have title + value + type
2. **Checklist-first** — always check before generating documents
3. **Re-check on change** — value/method/type changes may alter requirements
4. **Confirm deletes** — always ask before deleting
5. **Report backfills** — tell user if existing documents were auto-linked
6. **Status awareness** — track where the package is in the lifecycle

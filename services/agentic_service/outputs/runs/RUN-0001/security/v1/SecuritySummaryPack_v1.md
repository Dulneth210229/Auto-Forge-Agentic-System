# Security Summary Pack

**Run ID:** RUN-0001  
**Stage:** security  
**Version:** v1  
**Generated At:** 2026-05-03T00:23:10.529568+00:00  
**Target Path:** ./sample_ecommerce_app

---

## 1. Security Gate

| Field | Value |
|---|---|
| Status | **FAIL** |
| Reason | Security gate failed because Critical vulnerabilities were detected. |
| Policy | FAIL if one or more Critical findings exist. |

---

## 2. Severity Summary

| Severity | Count |
|---|---:|
| Critical | 6 |
| High | 15 |
| Medium | 12 |
| Low | 3 |
| **Total** | **36** |

---

## 3. Dashboard Counts

| Metric | Count |
|---|---:|
| Dependency Vulnerabilities | 27 |
| LLM Findings | 2 |
| Fix Suggestions | 36 |
| Top Blocking Findings | 10 |

---

## 4. Traceability

| Metric | Value |
|---|---:|
| Coverage Percentage | 100.0% |
| Mapped Findings | 36 |
| Total Findings | 36 |

---

## 5. Deduplication

| Metric | Value |
|---|---:|
| Before Deduplication | 50 |
| After Deduplication | 36 |
| Duplicates Removed | 14 |

---

## 6. Top Blocking Findings

| ID | Title | Severity | File | Method | Requirement | Module |
|---|---|---|---|---|---|---|
| SEC-001 | Hardcoded secret detected | High | sample_ecommerce_app\app.py | AST | FR-006 | admin |
| SEC-002 | Use of eval() detected | Critical | sample_ecommerce_app\app.py | AST | NFR-SEC-001 | general_security |
| SEC-003 | Unsafe subprocess usage with shell=True | High | sample_ecommerce_app\app.py | AST | NFR-SEC-001 | general_security |
| SEC-007 | Possible raw SQL string formatting | High | sample_ecommerce_app\app.py | AST | NFR-SEC-001 | general_security |
| SEC-008 | Direct innerHTML assignment detected | High | sample_ecommerce_app\frontend.js | AST | FR-007 | frontend |
| SEC-010 | JavaScript eval() usage detected | Critical | sample_ecommerce_app\frontend.js | AST | FR-007 | frontend |
| SEC-011 | Possible hardcoded secret detected | High | sample_ecommerce_app\.env | AST | FR-005 | authentication |
| SEC-015 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | Dependency | NFR-002 | dependency_management |
| SEC-016 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | Dependency | NFR-002 | dependency_management |
| SEC-017 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | Dependency | NFR-002 | dependency_management |

---

## 7. Artifact Paths

| Artifact | Path |
|---|---|
| Security Report JSON | outputs\runs\RUN-0001\security\v1\SecurityReport_v1.json |
| Security Report Markdown | outputs\runs\RUN-0001\security\v1\SecurityReport_v1.md |
| Summary Pack JSON | outputs\runs\RUN-0001\security\v1\SecuritySummaryPack_v1.json |
| Summary Pack Markdown | outputs\runs\RUN-0001\security\v1\SecuritySummaryPack_v1.md |

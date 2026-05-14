# Security Summary Pack

**Run ID:** RUN-0001  
**Stage:** security  
**Version:** v1  
**Generated At:** 2026-05-14T21:50:41.561970+00:00  
**Target Path:** outputs/runs/RUN-0001/code/v7/generated_app

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
| Critical | 1 |
| High | 4 |
| Medium | 2 |
| Low | 1 |
| **Total** | **8** |

---

## 3. Dashboard Counts

| Metric | Count |
|---|---:|
| Dependency Vulnerabilities | 10 |
| LLM Findings | 0 |
| Fix Suggestions | 8 |
| Top Blocking Findings | 5 |

---

## 4. Traceability

| Metric | Value |
|---|---:|
| Coverage Percentage | 100.0% |
| Mapped Findings | 8 |
| Total Findings | 8 |

---

## 5. Deduplication

| Metric | Value |
|---|---:|
| Before Deduplication | 10 |
| After Deduplication | 8 |
| Duplicates Removed | 2 |

---

## 6. Top Blocking Findings

| ID | Title | Severity | File | Method | Requirement | Module |
|---|---|---|---|---|---|---|
| SEC-003 | Vulnerable dependency detected: mongoose | Critical | outputs\runs\RUN-0001\code\v7\generated_app\backend\package.json | Dependency | FR-001 | catalog |
| SEC-004 | Vulnerable dependency detected: mongoose | High | outputs\runs\RUN-0001\code\v7\generated_app\backend\package.json | Dependency | FR-001 | catalog |
| SEC-005 | Vulnerable dependency detected: mongoose | High | outputs\runs\RUN-0001\code\v7\generated_app\backend\package.json | Dependency | NFR-002 | dependency_management |
| SEC-006 | Vulnerable dependency detected: vite | High | outputs\runs\RUN-0001\code\v7\generated_app\frontend\package.json | Dependency | NFR-002 | dependency_management |
| SEC-007 | Vulnerable dependency detected: vite | High | outputs\runs\RUN-0001\code\v7\generated_app\frontend\package.json | Dependency | NFR-002 | dependency_management |

---

## 7. Artifact Paths

| Artifact | Path |
|---|---|
| Security Report JSON | outputs\runs\RUN-0001\security\v1\SecurityReport_v1.json |
| Security Report Markdown | outputs\runs\RUN-0001\security\v1\SecurityReport_v1.md |
| Summary Pack JSON | outputs\runs\RUN-0001\security\v1\SecuritySummaryPack_v1.json |
| Summary Pack Markdown | outputs\runs\RUN-0001\security\v1\SecuritySummaryPack_v1.md |

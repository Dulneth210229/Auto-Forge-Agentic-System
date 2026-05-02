# Security Summary Pack

**Run ID:** RUN-API-TEST  
**Stage:** security  
**Version:** v1  
**Generated At:** 2026-05-02T23:43:05.006689+00:00  
**Target Path:** C:\Users\ASUS VivoBOOK\AppData\Local\Temp\pytest-of-ASUS VivoBOOK\pytest-16\test_security_run_endpoint_wit0\sample_app

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
| High | 1 |
| Medium | 0 |
| Low | 0 |
| **Total** | **2** |

---

## 3. Dashboard Counts

| Metric | Count |
|---|---:|
| Dependency Vulnerabilities | 0 |
| LLM Findings | 0 |
| Fix Suggestions | 2 |
| Top Blocking Findings | 2 |

---

## 4. Traceability

| Metric | Value |
|---|---:|
| Coverage Percentage | 100.0% |
| Mapped Findings | 2 |
| Total Findings | 2 |

---

## 5. Deduplication

| Metric | Value |
|---|---:|
| Before Deduplication | 3 |
| After Deduplication | 2 |
| Duplicates Removed | 1 |

---

## 6. Top Blocking Findings

| ID | Title | Severity | File | Method | Requirement | Module |
|---|---|---|---|---|---|---|
| SEC-001 | Hardcoded secret detected | High | C:\Users\ASUS VivoBOOK\AppData\Local\Temp\pytest-of-ASUS VivoBOOK\pytest-16\test_security_run_endpoint_wit0\sample_app\app.py | AST | FR-006 | admin |
| SEC-002 | Use of eval() detected | Critical | C:\Users\ASUS VivoBOOK\AppData\Local\Temp\pytest-of-ASUS VivoBOOK\pytest-16\test_security_run_endpoint_wit0\sample_app\app.py | AST | NFR-SEC-001 | general_security |

---

## 7. Artifact Paths

| Artifact | Path |
|---|---|
| Security Report JSON | outputs\runs\RUN-API-TEST\security\v1\SecurityReport_v1.json |
| Security Report Markdown | outputs\runs\RUN-API-TEST\security\v1\SecurityReport_v1.md |
| Summary Pack JSON | outputs\runs\RUN-API-TEST\security\v1\SecuritySummaryPack_v1.json |
| Summary Pack Markdown | outputs\runs\RUN-API-TEST\security\v1\SecuritySummaryPack_v1.md |

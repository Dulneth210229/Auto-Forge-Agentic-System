# Security Report

**Run ID:** RUN-0001  
**Stage:** security  
**Version:** v1

---

## 1. Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 1 |
| **Total** | **2** |

---

## 2. Security Gate Decision

| Field | Value |
|---|---|
| Status | **WARN** |
| Reason | Security gate warning because Medium severity findings were detected. |
| Policy | WARN if Medium findings exist and no Critical or blocking High findings exist. |

No blocking findings.

---

## 3. Findings

| ID | Title | Severity | File | Line | Method | CWE |
|---|---|---|---|---:|---|---|
| SEC-001 | Insecure CORS wildcard detected | Medium | outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py | 13 | AST | CWE-942 |
| SEC-002 | LLM review failed | Low | outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py | 0 | LLM | N/A |

---

## 4. Finding Details

### SEC-001 — Insecure CORS wildcard detected

**Severity:** Medium  
**Detection Method:** AST  
**File:** outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py  
**Line:** 13  
**CWE:** CWE-942

**Description:**  
Using wildcard CORS origins may allow untrusted websites to interact with the API.

**Recommendation:**  
Restrict CORS origins to trusted frontend domains.

**Traceability:**  
- Requirement ID: NFR-001
- API: N/A
- Module: security_configuration

### SEC-002 — LLM review failed

**Severity:** Low  
**Detection Method:** LLM  
**File:** outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py  
**Line:** 0  
**CWE:** N/A

**Description:**  
The LLM review failed for this file: the JSON object must be str, bytes or bytearray, not coroutine

**Recommendation:**  
Check Ollama availability and retry the LLM review.

**Traceability:**  
- Requirement ID: NFR-SEC-001
- API: N/A
- Module: general_security


---

## 5. Fix Suggestions

| Finding ID | Issue | Severity | Priority | Effort |
|---|---|---|---|---|
| SEC-001 | Insecure CORS wildcard detected | Medium | Normal | Medium |
| SEC-002 | LLM review failed | Low | Low | Medium |

### SEC-001 — Insecure CORS wildcard detected

**Severity:** Medium  
**File:** outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py  
**Priority:** Normal  
**Estimated Effort:** Medium

**Recommended Fix:**  
Remove eval/exec usage and replace it with safe parsing or explicit controlled logic.

**Example Fix:**

```txt
Use json.loads(user_input) for JSON data instead of eval(user_input).
```

### SEC-002 — LLM review failed

**Severity:** Low  
**File:** outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py  
**Priority:** Low  
**Estimated Effort:** Medium

**Recommended Fix:**  
Review the finding and apply a secure coding fix based on the recommendation.

**Example Fix:**

```txt
Check Ollama availability and retry the LLM review.
```


---

## 6. Dependency Vulnerabilities

No dependency vulnerabilities were detected.

---

## 7. LLM Findings

| Title | Severity | File | Line | CWE | Confidence |
|---|---|---|---:|---|---:|
| LLM review failed | Low | outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py | 0 | N/A | 0.0 |

### LLM review failed

**Severity:** Low  
**File:** outputs\runs\RUN-0001\code\v1\generated_app\backend\main.py  
**Line:** 0  
**CWE:** N/A  
**Confidence:** 0.0  
**Source:** ollama

**Description:**  
The LLM review failed for this file: the JSON object must be str, bytes or bytearray, not coroutine

**Recommendation:**  
Check Ollama availability and retry the LLM review.


---

## 8. Metrics

| Metric | Value |
|---|---:|
| Coverage | 1.0 |
| Confidence | 0.85 |
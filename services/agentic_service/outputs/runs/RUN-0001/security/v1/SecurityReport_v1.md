# Security Report

**Run ID:** RUN-0001  
**Stage:** security  
**Version:** v1

---

## 1. Summary

| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 5 |
| Medium | 3 |
| Low | 0 |
| **Total** | **9** |

---

## 2. Findings

| ID | Title | Severity | File | Line | Method | CWE |
|---|---|---|---|---:|---|---|
| SEC-001 | Hardcoded secret detected | High | sample_ecommerce_app\app.py | 8 | AST | CWE-798 |
| SEC-002 | Hardcoded secret detected | High | sample_ecommerce_app\app.py | 9 | AST | CWE-798 |
| SEC-003 | Hardcoded secret detected | High | sample_ecommerce_app\app.py | 10 | AST | CWE-798 |
| SEC-004 | Use of eval() detected | Critical | sample_ecommerce_app\app.py | 42 | AST | CWE-95 |
| SEC-005 | Unsafe subprocess usage with shell=True | High | sample_ecommerce_app\app.py | 47 | AST | CWE-78 |
| SEC-006 | Weak hashing algorithm detected | Medium | sample_ecommerce_app\app.py | 37 | AST | CWE-327 |
| SEC-007 | Debug mode enabled | Medium | sample_ecommerce_app\app.py | 6 | AST | CWE-489 |
| SEC-008 | Insecure CORS wildcard detected | Medium | sample_ecommerce_app\app.py | 14 | AST | CWE-942 |
| SEC-009 | Possible raw SQL string formatting | High | sample_ecommerce_app\app.py | 31 | AST | CWE-89 |

---

## 3. Finding Details

### SEC-001 — Hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 8  
**CWE:** CWE-798

**Description:**  
The variable 'SECRET_KEY' appears to contain a hardcoded secret.

**Recommendation:**  
Move secrets to environment variables or a secure secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-002 — Hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 9  
**CWE:** CWE-798

**Description:**  
The variable 'API_KEY' appears to contain a hardcoded secret.

**Recommendation:**  
Move secrets to environment variables or a secure secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-003 — Hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 10  
**CWE:** CWE-798

**Description:**  
The variable 'DB_PASSWORD' appears to contain a hardcoded secret.

**Recommendation:**  
Move secrets to environment variables or a secure secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-004 — Use of eval() detected

**Severity:** Critical  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 42  
**CWE:** CWE-95

**Description:**  
The eval() function can execute arbitrary code and may lead to remote code execution.

**Recommendation:**  
Avoid eval(). Use safe parsing or explicit logic instead.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-005 — Unsafe subprocess usage with shell=True

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 47  
**CWE:** CWE-78

**Description:**  
Using subprocess with shell=True may allow command injection.

**Recommendation:**  
Use shell=False and pass command arguments as a list.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-006 — Weak hashing algorithm detected

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 37  
**CWE:** CWE-327

**Description:**  
The code uses hashlib.md5, which is considered weak for security-sensitive hashing.

**Recommendation:**  
Use SHA-256, SHA-512, bcrypt, Argon2, or another secure hashing approach depending on the use case.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-007 — Debug mode enabled

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 6  
**CWE:** CWE-489

**Description:**  
Debug mode may expose sensitive stack traces and internal application information.

**Recommendation:**  
Disable debug mode in production environments.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-008 — Insecure CORS wildcard detected

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 14  
**CWE:** CWE-942

**Description:**  
Using wildcard CORS origins may allow untrusted websites to interact with the API.

**Recommendation:**  
Restrict CORS origins to trusted frontend domains.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-009 — Possible raw SQL string formatting

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 31  
**CWE:** CWE-89

**Description:**  
SQL queries built using string formatting or concatenation may cause SQL injection.

**Recommendation:**  
Use parameterized queries or an ORM query builder.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 


---

## 4. Dependency Vulnerabilities

No dependency vulnerabilities were recorded in this skeleton version.

---

## 5. LLM Findings

No LLM-assisted findings were recorded in this skeleton version.

---

## 6. Metrics

| Metric | Value |
|---|---:|
| Coverage | 1.0 |
| Confidence | 0.8 |

---

## 7. Notes

This is the initial Security Agent skeleton report.  
Real AST scanning, dependency scanning, and LLM-assisted secure code review will be added in later steps.
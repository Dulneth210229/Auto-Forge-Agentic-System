# Security Report

**Run ID:** RUN-0001  
**Stage:** security  
**Version:** v1

---

## 1. Summary

| Severity | Count |
|---|---:|
| Critical | 7 |
| High | 22 |
| Medium | 18 |
| Low | 1 |
| **Total** | **48** |

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
| SEC-010 | Direct innerHTML assignment detected | High | sample_ecommerce_app\frontend.js | 2 | AST | CWE-79 |
| SEC-011 | Sensitive token stored in localStorage | Medium | sample_ecommerce_app\frontend.js | 6 | AST | CWE-922 |
| SEC-012 | JavaScript eval() usage detected | Critical | sample_ecommerce_app\frontend.js | 10 | AST | CWE-95 |
| SEC-013 | Sensitive data logged to console | Medium | sample_ecommerce_app\frontend.js | 13 | AST | CWE-532 |
| SEC-014 | Possible hardcoded secret detected | High | sample_ecommerce_app\.env | 2 | AST | CWE-798 |
| SEC-015 | Possible hardcoded secret detected | High | sample_ecommerce_app\.env | 3 | AST | CWE-798 |
| SEC-016 | Possible hardcoded secret detected | High | sample_ecommerce_app\app.py | 8 | AST | CWE-798 |
| SEC-017 | Possible hardcoded secret detected | High | sample_ecommerce_app\app.py | 9 | AST | CWE-798 |
| SEC-018 | Possible hardcoded secret detected | High | sample_ecommerce_app\app.py | 10 | AST | CWE-798 |
| SEC-019 | Debug configuration enabled | Medium | sample_ecommerce_app\.env | 1 | AST | CWE-489 |
| SEC-020 | Wildcard CORS setting in configuration | Medium | sample_ecommerce_app\.env | 4 | AST | CWE-942 |
| SEC-021 | Docker container runs as root | Medium | sample_ecommerce_app\Dockerfile | 7 | AST | CWE-250 |
| SEC-022 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-77 |
| SEC-023 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-1321 |
| SEC-024 | Vulnerable dependency detected: lodash | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-94 |
| SEC-025 | Vulnerable dependency detected: lodash | Medium | sample_ecommerce_app\package.json | 0 | Dependency | CWE-1333 |
| SEC-026 | Vulnerable dependency detected: lodash | Medium | sample_ecommerce_app\package.json | 0 | Dependency | CWE-1321 |
| SEC-027 | Vulnerable dependency detected: axios | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-20 |
| SEC-028 | Vulnerable dependency detected: axios | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-754 |
| SEC-029 | Vulnerable dependency detected: axios | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-1333 |
| SEC-030 | Vulnerable dependency detected: axios | High | sample_ecommerce_app\package.json | 0 | Dependency | CWE-918 |
| SEC-031 | Vulnerable dependency detected: axios | Medium | sample_ecommerce_app\package.json | 0 | Dependency | CWE-441 |
| SEC-032 | Vulnerable dependency detected: express | Medium | sample_ecommerce_app\package.json | 0 | Dependency | CWE-1286 |
| SEC-033 | Vulnerable dependency detected: express | Low | sample_ecommerce_app\package.json | 0 | Dependency | CWE-79 |
| SEC-034 | Vulnerable dependency detected: django | Critical | sample_ecommerce_app\requirements.txt | 1 | Dependency | CWE-79 |
| SEC-035 | Vulnerable dependency detected: django | Critical | sample_ecommerce_app\requirements.txt | 1 | Dependency | CWE-22 |
| SEC-036 | Vulnerable dependency detected: django | Critical | sample_ecommerce_app\requirements.txt | 1 | Dependency | CWE-89 |
| SEC-037 | Vulnerable dependency detected: django | Critical | sample_ecommerce_app\requirements.txt | 1 | Dependency | CWE-89 |
| SEC-038 | Vulnerable dependency detected: django | Critical | sample_ecommerce_app\requirements.txt | 1 | Dependency | CWE-94 |
| SEC-039 | Vulnerable dependency detected: flask | High | sample_ecommerce_app\requirements.txt | 2 | Dependency | CWE-20 |
| SEC-040 | Vulnerable dependency detected: flask | High | sample_ecommerce_app\requirements.txt | 2 | Dependency | CWE-400 |
| SEC-041 | Vulnerable dependency detected: flask | High | sample_ecommerce_app\requirements.txt | 2 | Dependency | CWE-539 |
| SEC-042 | Vulnerable dependency detected: flask | Medium | sample_ecommerce_app\requirements.txt | 2 | Dependency | CWE-937 |
| SEC-043 | Vulnerable dependency detected: flask | Medium | sample_ecommerce_app\requirements.txt | 2 | Dependency | CWE-937 |
| SEC-044 | Vulnerable dependency detected: requests | High | sample_ecommerce_app\requirements.txt | 3 | Dependency | CWE-522 |
| SEC-045 | Vulnerable dependency detected: requests | Medium | sample_ecommerce_app\requirements.txt | 3 | Dependency | CWE-522 |
| SEC-046 | Vulnerable dependency detected: requests | Medium | sample_ecommerce_app\requirements.txt | 3 | Dependency | CWE-200 |
| SEC-047 | Vulnerable dependency detected: requests | Medium | sample_ecommerce_app\requirements.txt | 3 | Dependency | CWE-937 |
| SEC-048 | Vulnerable dependency detected: requests | Medium | sample_ecommerce_app\requirements.txt | 3 | Dependency | CWE-937 |

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
The code uses hashlib.md5, which is weak for security-sensitive hashing.

**Recommendation:**  
Use SHA-256, bcrypt, Argon2, or another secure hashing approach.

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

### SEC-010 — Direct innerHTML assignment detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\frontend.js  
**Line:** 2  
**CWE:** CWE-79

**Description:**  
Assigning content to innerHTML may introduce XSS if the content includes user input.

**Recommendation:**  
Use textContent or sanitize HTML before assigning it to the DOM.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-011 — Sensitive token stored in localStorage

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\frontend.js  
**Line:** 6  
**CWE:** CWE-922

**Description:**  
Storing authentication tokens in localStorage can increase exposure to XSS attacks.

**Recommendation:**  
Prefer secure, HttpOnly cookies for sensitive session tokens.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-012 — JavaScript eval() usage detected

**Severity:** Critical  
**Detection Method:** AST  
**File:** sample_ecommerce_app\frontend.js  
**Line:** 10  
**CWE:** CWE-95

**Description:**  
JavaScript eval() can execute arbitrary code and may lead to code injection.

**Recommendation:**  
Avoid eval(). Use safe parsing or explicit logic instead.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-013 — Sensitive data logged to console

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\frontend.js  
**Line:** 13  
**CWE:** CWE-532

**Description:**  
Logging secrets or tokens can expose sensitive information in logs.

**Recommendation:**  
Remove sensitive data from logs.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-014 — Possible hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\.env  
**Line:** 2  
**CWE:** CWE-798

**Description:**  
A possible hardcoded secret, password, token, or API key was found in a text-based file.

**Recommendation:**  
Move secrets to environment variables or a dedicated secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-015 — Possible hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\.env  
**Line:** 3  
**CWE:** CWE-798

**Description:**  
A possible hardcoded secret, password, token, or API key was found in a text-based file.

**Recommendation:**  
Move secrets to environment variables or a dedicated secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-016 — Possible hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 8  
**CWE:** CWE-798

**Description:**  
A possible hardcoded secret, password, token, or API key was found in a text-based file.

**Recommendation:**  
Move secrets to environment variables or a dedicated secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-017 — Possible hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 9  
**CWE:** CWE-798

**Description:**  
A possible hardcoded secret, password, token, or API key was found in a text-based file.

**Recommendation:**  
Move secrets to environment variables or a dedicated secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-018 — Possible hardcoded secret detected

**Severity:** High  
**Detection Method:** AST  
**File:** sample_ecommerce_app\app.py  
**Line:** 10  
**CWE:** CWE-798

**Description:**  
A possible hardcoded secret, password, token, or API key was found in a text-based file.

**Recommendation:**  
Move secrets to environment variables or a dedicated secret manager.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-019 — Debug configuration enabled

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\.env  
**Line:** 1  
**CWE:** CWE-489

**Description:**  
Debug mode appears to be enabled in a configuration file.

**Recommendation:**  
Disable debug mode in production configurations.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-020 — Wildcard CORS setting in configuration

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\.env  
**Line:** 4  
**CWE:** CWE-942

**Description:**  
Wildcard CORS configuration may allow untrusted origins to interact with the application.

**Recommendation:**  
Restrict CORS settings to trusted frontend origins.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-021 — Docker container runs as root

**Severity:** Medium  
**Detection Method:** AST  
**File:** sample_ecommerce_app\Dockerfile  
**Line:** 7  
**CWE:** CWE-250

**Description:**  
Running containers as root increases the impact of container compromise.

**Recommendation:**  
Create and use a non-root user inside the Docker image.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-022 — Vulnerable dependency detected: lodash

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-77

**Description:**  
Command Injection in lodash Package: lodash, Version: 4.17.15, Ecosystem: npm, Vulnerability ID: GHSA-35jh-r3h4-6jhm.

**Recommendation:**  
Review GHSA-35jh-r3h4-6jhm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-023 — Vulnerable dependency detected: lodash

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-1321

**Description:**  
Prototype Pollution in lodash Package: lodash, Version: 4.17.15, Ecosystem: npm, Vulnerability ID: GHSA-p6mc-m468-83gw.

**Recommendation:**  
Review GHSA-p6mc-m468-83gw in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-024 — Vulnerable dependency detected: lodash

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-94

**Description:**  
lodash vulnerable to Code Injection via `_.template` imports key names Package: lodash, Version: 4.17.15, Ecosystem: npm, Vulnerability ID: GHSA-r5fr-rjxr-66jc.

**Recommendation:**  
Review GHSA-r5fr-rjxr-66jc in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-025 — Vulnerable dependency detected: lodash

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-1333

**Description:**  
Regular Expression Denial of Service (ReDoS) in lodash Package: lodash, Version: 4.17.15, Ecosystem: npm, Vulnerability ID: GHSA-29mw-wpgm-hmr9.

**Recommendation:**  
Review GHSA-29mw-wpgm-hmr9 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-026 — Vulnerable dependency detected: lodash

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-1321

**Description:**  
lodash vulnerable to Prototype Pollution via array path bypass in `_.unset` and `_.omit` Package: lodash, Version: 4.17.15, Ecosystem: npm, Vulnerability ID: GHSA-f23m-r3pf-42rh.

**Recommendation:**  
Review GHSA-f23m-r3pf-42rh in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-027 — Vulnerable dependency detected: axios

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-20

**Description:**  
Denial of Service in axios Package: axios, Version: 0.18.0, Ecosystem: npm, Vulnerability ID: GHSA-42xw-2xvc-qx8m.

**Recommendation:**  
Review GHSA-42xw-2xvc-qx8m in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-028 — Vulnerable dependency detected: axios

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-754

**Description:**  
Axios is Vulnerable to Denial of Service via __proto__ Key in mergeConfig Package: axios, Version: 0.18.0, Ecosystem: npm, Vulnerability ID: GHSA-43fc-jf86-j433.

**Recommendation:**  
Review GHSA-43fc-jf86-j433 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-029 — Vulnerable dependency detected: axios

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-1333

**Description:**  
axios Inefficient Regular Expression Complexity vulnerability Package: axios, Version: 0.18.0, Ecosystem: npm, Vulnerability ID: GHSA-cph5-m8f7-6c5x.

**Recommendation:**  
Review GHSA-cph5-m8f7-6c5x in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-030 — Vulnerable dependency detected: axios

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-918

**Description:**  
axios Requests Vulnerable To Possible SSRF and Credential Leakage via Absolute URL Package: axios, Version: 0.18.0, Ecosystem: npm, Vulnerability ID: GHSA-jr5f-v2jv-69x6.

**Recommendation:**  
Review GHSA-jr5f-v2jv-69x6 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-031 — Vulnerable dependency detected: axios

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-441

**Description:**  
Axios has a NO_PROXY Hostname Normalization Bypass that Leads to SSRF Package: axios, Version: 0.18.0, Ecosystem: npm, Vulnerability ID: GHSA-3p68-rc4w-qgx5.

**Recommendation:**  
Review GHSA-3p68-rc4w-qgx5 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-032 — Vulnerable dependency detected: express

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-1286

**Description:**  
Express.js Open Redirect in malformed URLs Package: express, Version: 4.16.0, Ecosystem: npm, Vulnerability ID: GHSA-rv95-896h-c2vc.

**Recommendation:**  
Review GHSA-rv95-896h-c2vc in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-033 — Vulnerable dependency detected: express

**Severity:** Low  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\package.json  
**Line:** 0  
**CWE:** CWE-79

**Description:**  
express vulnerable to XSS via response.redirect() Package: express, Version: 4.16.0, Ecosystem: npm, Vulnerability ID: GHSA-qw6h-vgh9-j6wx.

**Recommendation:**  
Review GHSA-qw6h-vgh9-j6wx in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-034 — Vulnerable dependency detected: django

**Severity:** Critical  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 1  
**CWE:** CWE-79

**Description:**  
Django Allows Redirect via Data URL Package: django, Version: 1.2, Ecosystem: PyPI, Vulnerability ID: GHSA-78vx-ggch-wghm.

**Recommendation:**  
Review GHSA-78vx-ggch-wghm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-035 — Vulnerable dependency detected: django

**Severity:** Critical  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 1  
**CWE:** CWE-22

**Description:**  
Directory traversal in Django Package: django, Version: 1.2, Ecosystem: PyPI, Vulnerability ID: GHSA-7g9h-c88w-r7h2.

**Recommendation:**  
Review GHSA-7g9h-c88w-r7h2 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-036 — Vulnerable dependency detected: django

**Severity:** Critical  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 1  
**CWE:** CWE-89

**Description:**  
Django vulnerable to SQL injection via _connector keyword argument in QuerySet and Q objects. Package: django, Version: 1.2, Ecosystem: PyPI, Vulnerability ID: GHSA-frmv-pr5f-9mcr.

**Recommendation:**  
Review GHSA-frmv-pr5f-9mcr in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-037 — Vulnerable dependency detected: django

**Severity:** Critical  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 1  
**CWE:** CWE-89

**Description:**  
SQL injection in Django Package: django, Version: 1.2, Ecosystem: PyPI, Vulnerability ID: GHSA-hmr4-m2h5-33qx.

**Recommendation:**  
Review GHSA-hmr4-m2h5-33qx in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-038 — Vulnerable dependency detected: django

**Severity:** Critical  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 1  
**CWE:** CWE-94

**Description:**  
Code Injection in Django Package: django, Version: 1.2, Ecosystem: PyPI, Vulnerability ID: GHSA-rvq6-mrpv-m6rm.

**Recommendation:**  
Review GHSA-rvq6-mrpv-m6rm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-039 — Vulnerable dependency detected: flask

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 2  
**CWE:** CWE-20

**Description:**  
Flask is vulnerable to Denial of Service via incorrect encoding of JSON data Package: flask, Version: 0.12, Ecosystem: PyPI, Vulnerability ID: GHSA-562c-5r94-xh97.

**Recommendation:**  
Review GHSA-562c-5r94-xh97 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-040 — Vulnerable dependency detected: flask

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 2  
**CWE:** CWE-400

**Description:**  
Pallets Project Flask is vulnerable to Denial of Service via Unexpected memory usage Package: flask, Version: 0.12, Ecosystem: PyPI, Vulnerability ID: GHSA-5wv5-4vpf-pj6m.

**Recommendation:**  
Review GHSA-5wv5-4vpf-pj6m in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-041 — Vulnerable dependency detected: flask

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 2  
**CWE:** CWE-539

**Description:**  
Flask vulnerable to possible disclosure of permanent session cookie due to missing Vary: Cookie header Package: flask, Version: 0.12, Ecosystem: PyPI, Vulnerability ID: GHSA-m2qf-hxjv-5gpq.

**Recommendation:**  
Review GHSA-m2qf-hxjv-5gpq in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-042 — Vulnerable dependency detected: flask

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 2  
**CWE:** CWE-937

**Description:**  
The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083. Package: flask, Version: 0.12, Ecosystem: PyPI, Vulnerability ID: PYSEC-2018-66.

**Recommendation:**  
Review PYSEC-2018-66 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-043 — Vulnerable dependency detected: flask

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 2  
**CWE:** CWE-937

**Description:**  
The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656. Package: flask, Version: 0.12, Ecosystem: PyPI, Vulnerability ID: PYSEC-2019-179.

**Recommendation:**  
Review PYSEC-2019-179 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-044 — Vulnerable dependency detected: requests

**Severity:** High  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 3  
**CWE:** CWE-522

**Description:**  
Insufficiently Protected Credentials in Requests Package: requests, Version: 2.19.0, Ecosystem: PyPI, Vulnerability ID: GHSA-x84v-xcm2-53pg.

**Recommendation:**  
Review GHSA-x84v-xcm2-53pg in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-045 — Vulnerable dependency detected: requests

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 3  
**CWE:** CWE-522

**Description:**  
Requests vulnerable to .netrc credentials leak via malicious URLs Package: requests, Version: 2.19.0, Ecosystem: PyPI, Vulnerability ID: GHSA-9hjg-9r4m-mvj7.

**Recommendation:**  
Review GHSA-9hjg-9r4m-mvj7 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-046 — Vulnerable dependency detected: requests

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 3  
**CWE:** CWE-200

**Description:**  
Unintended leak of Proxy-Authorization header in requests Package: requests, Version: 2.19.0, Ecosystem: PyPI, Vulnerability ID: GHSA-j8r2-6x86-q33q.

**Recommendation:**  
Review GHSA-j8r2-6x86-q33q in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-047 — Vulnerable dependency detected: requests

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 3  
**CWE:** CWE-937

**Description:**  
The Requests package before 2.20.0 for Python sends an HTTP Authorization header to an http URI upon receiving a same-hostname https-to-http redirect, which makes it easier for remote attackers to discover credentials by sniffing the network. Package: requests, Version: 2.19.0, Ecosystem: PyPI, Vulnerability ID: PYSEC-2018-28.

**Recommendation:**  
Review PYSEC-2018-28 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 

### SEC-048 — Vulnerable dependency detected: requests

**Severity:** Medium  
**Detection Method:** Dependency  
**File:** sample_ecommerce_app\requirements.txt  
**Line:** 3  
**CWE:** CWE-937

**Description:**  
Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.31.0.

 Package: requests, Version: 2.19.0, Ecosystem: PyPI, Vulnerability ID: PYSEC-2023-74.

**Recommendation:**  
Review PYSEC-2023-74 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

**Traceability:**  
- Requirement ID: 
- API: 
- Module: 


---

## 4. Dependency Vulnerabilities

| Vulnerability ID | Package | Version | Ecosystem | Severity | CWE | Source |
|---|---|---|---|---|---|---|
| GHSA-35jh-r3h4-6jhm | lodash | 4.17.15 | npm | High | CWE-77 | osv.dev |
| GHSA-p6mc-m468-83gw | lodash | 4.17.15 | npm | High | CWE-1321 | osv.dev |
| GHSA-r5fr-rjxr-66jc | lodash | 4.17.15 | npm | High | CWE-94 | osv.dev |
| GHSA-29mw-wpgm-hmr9 | lodash | 4.17.15 | npm | Medium | CWE-1333 | osv.dev |
| GHSA-f23m-r3pf-42rh | lodash | 4.17.15 | npm | Medium | CWE-1321 | osv.dev |
| GHSA-42xw-2xvc-qx8m | axios | 0.18.0 | npm | High | CWE-20 | osv.dev |
| GHSA-43fc-jf86-j433 | axios | 0.18.0 | npm | High | CWE-754 | osv.dev |
| GHSA-cph5-m8f7-6c5x | axios | 0.18.0 | npm | High | CWE-1333 | osv.dev |
| GHSA-jr5f-v2jv-69x6 | axios | 0.18.0 | npm | High | CWE-918 | osv.dev |
| GHSA-3p68-rc4w-qgx5 | axios | 0.18.0 | npm | Medium | CWE-441 | osv.dev |
| GHSA-rv95-896h-c2vc | express | 4.16.0 | npm | Medium | CWE-1286 | osv.dev |
| GHSA-qw6h-vgh9-j6wx | express | 4.16.0 | npm | Low | CWE-79 | osv.dev |
| GHSA-78vx-ggch-wghm | django | 1.2 | PyPI | Critical | CWE-79 | osv.dev |
| GHSA-7g9h-c88w-r7h2 | django | 1.2 | PyPI | Critical | CWE-22 | osv.dev |
| GHSA-frmv-pr5f-9mcr | django | 1.2 | PyPI | Critical | CWE-89 | osv.dev |
| GHSA-hmr4-m2h5-33qx | django | 1.2 | PyPI | Critical | CWE-89 | osv.dev |
| GHSA-rvq6-mrpv-m6rm | django | 1.2 | PyPI | Critical | CWE-94 | osv.dev |
| GHSA-562c-5r94-xh97 | flask | 0.12 | PyPI | High | CWE-20 | osv.dev |
| GHSA-5wv5-4vpf-pj6m | flask | 0.12 | PyPI | High | CWE-400 | osv.dev |
| GHSA-m2qf-hxjv-5gpq | flask | 0.12 | PyPI | High | CWE-539 | osv.dev |
| PYSEC-2018-66 | flask | 0.12 | PyPI | Medium | CWE-937 | osv.dev |
| PYSEC-2019-179 | flask | 0.12 | PyPI | Medium | CWE-937 | osv.dev |
| GHSA-x84v-xcm2-53pg | requests | 2.19.0 | PyPI | High | CWE-522 | osv.dev |
| GHSA-9hjg-9r4m-mvj7 | requests | 2.19.0 | PyPI | Medium | CWE-522 | osv.dev |
| GHSA-j8r2-6x86-q33q | requests | 2.19.0 | PyPI | Medium | CWE-200 | osv.dev |
| PYSEC-2018-28 | requests | 2.19.0 | PyPI | Medium | CWE-937 | osv.dev |
| PYSEC-2023-74 | requests | 2.19.0 | PyPI | Medium | CWE-937 | osv.dev |

### GHSA-35jh-r3h4-6jhm — lodash 4.17.15

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-77  
**Source:** osv.dev

**Description:**  
Command Injection in lodash

**Recommendation:**  
Review GHSA-35jh-r3h4-6jhm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-p6mc-m468-83gw — lodash 4.17.15

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-1321  
**Source:** osv.dev

**Description:**  
Prototype Pollution in lodash

**Recommendation:**  
Review GHSA-p6mc-m468-83gw in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-r5fr-rjxr-66jc — lodash 4.17.15

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-94  
**Source:** osv.dev

**Description:**  
lodash vulnerable to Code Injection via `_.template` imports key names

**Recommendation:**  
Review GHSA-r5fr-rjxr-66jc in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-29mw-wpgm-hmr9 — lodash 4.17.15

**Ecosystem:** npm  
**Severity:** Medium  
**CWE:** CWE-1333  
**Source:** osv.dev

**Description:**  
Regular Expression Denial of Service (ReDoS) in lodash

**Recommendation:**  
Review GHSA-29mw-wpgm-hmr9 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-f23m-r3pf-42rh — lodash 4.17.15

**Ecosystem:** npm  
**Severity:** Medium  
**CWE:** CWE-1321  
**Source:** osv.dev

**Description:**  
lodash vulnerable to Prototype Pollution via array path bypass in `_.unset` and `_.omit`

**Recommendation:**  
Review GHSA-f23m-r3pf-42rh in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-42xw-2xvc-qx8m — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-20  
**Source:** osv.dev

**Description:**  
Denial of Service in axios

**Recommendation:**  
Review GHSA-42xw-2xvc-qx8m in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-43fc-jf86-j433 — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-754  
**Source:** osv.dev

**Description:**  
Axios is Vulnerable to Denial of Service via __proto__ Key in mergeConfig

**Recommendation:**  
Review GHSA-43fc-jf86-j433 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-cph5-m8f7-6c5x — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-1333  
**Source:** osv.dev

**Description:**  
axios Inefficient Regular Expression Complexity vulnerability

**Recommendation:**  
Review GHSA-cph5-m8f7-6c5x in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-jr5f-v2jv-69x6 — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-918  
**Source:** osv.dev

**Description:**  
axios Requests Vulnerable To Possible SSRF and Credential Leakage via Absolute URL

**Recommendation:**  
Review GHSA-jr5f-v2jv-69x6 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-3p68-rc4w-qgx5 — axios 0.18.0

**Ecosystem:** npm  
**Severity:** Medium  
**CWE:** CWE-441  
**Source:** osv.dev

**Description:**  
Axios has a NO_PROXY Hostname Normalization Bypass that Leads to SSRF

**Recommendation:**  
Review GHSA-3p68-rc4w-qgx5 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-rv95-896h-c2vc — express 4.16.0

**Ecosystem:** npm  
**Severity:** Medium  
**CWE:** CWE-1286  
**Source:** osv.dev

**Description:**  
Express.js Open Redirect in malformed URLs

**Recommendation:**  
Review GHSA-rv95-896h-c2vc in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-qw6h-vgh9-j6wx — express 4.16.0

**Ecosystem:** npm  
**Severity:** Low  
**CWE:** CWE-79  
**Source:** osv.dev

**Description:**  
express vulnerable to XSS via response.redirect()

**Recommendation:**  
Review GHSA-qw6h-vgh9-j6wx in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-78vx-ggch-wghm — django 1.2

**Ecosystem:** PyPI  
**Severity:** Critical  
**CWE:** CWE-79  
**Source:** osv.dev

**Description:**  
Django Allows Redirect via Data URL

**Recommendation:**  
Review GHSA-78vx-ggch-wghm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-7g9h-c88w-r7h2 — django 1.2

**Ecosystem:** PyPI  
**Severity:** Critical  
**CWE:** CWE-22  
**Source:** osv.dev

**Description:**  
Directory traversal in Django

**Recommendation:**  
Review GHSA-7g9h-c88w-r7h2 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-frmv-pr5f-9mcr — django 1.2

**Ecosystem:** PyPI  
**Severity:** Critical  
**CWE:** CWE-89  
**Source:** osv.dev

**Description:**  
Django vulnerable to SQL injection via _connector keyword argument in QuerySet and Q objects.

**Recommendation:**  
Review GHSA-frmv-pr5f-9mcr in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-hmr4-m2h5-33qx — django 1.2

**Ecosystem:** PyPI  
**Severity:** Critical  
**CWE:** CWE-89  
**Source:** osv.dev

**Description:**  
SQL injection in Django

**Recommendation:**  
Review GHSA-hmr4-m2h5-33qx in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-rvq6-mrpv-m6rm — django 1.2

**Ecosystem:** PyPI  
**Severity:** Critical  
**CWE:** CWE-94  
**Source:** osv.dev

**Description:**  
Code Injection in Django

**Recommendation:**  
Review GHSA-rvq6-mrpv-m6rm in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-562c-5r94-xh97 — flask 0.12

**Ecosystem:** PyPI  
**Severity:** High  
**CWE:** CWE-20  
**Source:** osv.dev

**Description:**  
Flask is vulnerable to Denial of Service via incorrect encoding of JSON data

**Recommendation:**  
Review GHSA-562c-5r94-xh97 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-5wv5-4vpf-pj6m — flask 0.12

**Ecosystem:** PyPI  
**Severity:** High  
**CWE:** CWE-400  
**Source:** osv.dev

**Description:**  
Pallets Project Flask is vulnerable to Denial of Service via Unexpected memory usage

**Recommendation:**  
Review GHSA-5wv5-4vpf-pj6m in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-m2qf-hxjv-5gpq — flask 0.12

**Ecosystem:** PyPI  
**Severity:** High  
**CWE:** CWE-539  
**Source:** osv.dev

**Description:**  
Flask vulnerable to possible disclosure of permanent session cookie due to missing Vary: Cookie header

**Recommendation:**  
Review GHSA-m2qf-hxjv-5gpq in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### PYSEC-2018-66 — flask 0.12

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-937  
**Source:** osv.dev

**Description:**  
The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.

**Recommendation:**  
Review PYSEC-2018-66 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### PYSEC-2019-179 — flask 0.12

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-937  
**Source:** osv.dev

**Description:**  
The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.

**Recommendation:**  
Review PYSEC-2019-179 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-x84v-xcm2-53pg — requests 2.19.0

**Ecosystem:** PyPI  
**Severity:** High  
**CWE:** CWE-522  
**Source:** osv.dev

**Description:**  
Insufficiently Protected Credentials in Requests

**Recommendation:**  
Review GHSA-x84v-xcm2-53pg in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-9hjg-9r4m-mvj7 — requests 2.19.0

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-522  
**Source:** osv.dev

**Description:**  
Requests vulnerable to .netrc credentials leak via malicious URLs

**Recommendation:**  
Review GHSA-9hjg-9r4m-mvj7 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-j8r2-6x86-q33q — requests 2.19.0

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-200  
**Source:** osv.dev

**Description:**  
Unintended leak of Proxy-Authorization header in requests

**Recommendation:**  
Review GHSA-j8r2-6x86-q33q in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### PYSEC-2018-28 — requests 2.19.0

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-937  
**Source:** osv.dev

**Description:**  
The Requests package before 2.20.0 for Python sends an HTTP Authorization header to an http URI upon receiving a same-hostname https-to-http redirect, which makes it easier for remote attackers to discover credentials by sniffing the network.

**Recommendation:**  
Review PYSEC-2018-28 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### PYSEC-2023-74 — requests 2.19.0

**Ecosystem:** PyPI  
**Severity:** Medium  
**CWE:** CWE-937  
**Source:** osv.dev

**Description:**  
Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.31.0.



**Recommendation:**  
Review PYSEC-2023-74 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.


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
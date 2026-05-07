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
| Low | 0 |
| **Total** | **1** |

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


---

## 5. Fix Suggestions

| Finding ID | Issue | Severity | Priority | Effort |
|---|---|---|---|---|
| SEC-001 | Insecure CORS wildcard detected | Medium | Normal | Medium |

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


---

## 6. Dependency Vulnerabilities

| Vulnerability ID | Package | Version | Ecosystem | Severity | CWE | Source |
|---|---|---|---|---|---|---|
| GHSA-35jh-r3h4-6jhm | lodash | 4.17.15 | npm | High | CWE-77 | osv.dev |
| GHSA-p6mc-m468-83gw | lodash | 4.17.15 | npm | High | CWE-1321 | osv.dev |
| GHSA-r5fr-rjxr-66jc | lodash | 4.17.15 | npm | High | CWE-94 | osv.dev |
| GHSA-29mw-wpgm-hmr9 | lodash | 4.17.15 | npm | Medium | CWE-1333 | osv.dev |
| GHSA-f23m-r3pf-42rh | lodash | 4.17.15 | npm | Medium | CWE-1321 | osv.dev |
| GHSA-42xw-2xvc-qx8m | axios | 0.18.0 | npm | High | CWE-20 | osv.dev |
| GHSA-43fc-jf86-j433 | axios | 0.18.0 | npm | High | CWE-754 | osv.dev |
| GHSA-62hf-57xw-28j9 | axios | 0.18.0 | npm | High | CWE-674 | osv.dev |
| GHSA-6chq-wfr3-2hj9 | axios | 0.18.0 | npm | High | CWE-113 | osv.dev |
| GHSA-cph5-m8f7-6c5x | axios | 0.18.0 | npm | High | CWE-1333 | osv.dev |
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

### GHSA-62hf-57xw-28j9 — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-674  
**Source:** osv.dev

**Description:**  
Axios: unbounded recursion in toFormData causes DoS via deeply nested request data

**Recommendation:**  
Review GHSA-62hf-57xw-28j9 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-6chq-wfr3-2hj9 — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-113  
**Source:** osv.dev

**Description:**  
Axios: Header Injection via Prototype Pollution

**Recommendation:**  
Review GHSA-6chq-wfr3-2hj9 in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

### GHSA-cph5-m8f7-6c5x — axios 0.18.0

**Ecosystem:** npm  
**Severity:** High  
**CWE:** CWE-1333  
**Source:** osv.dev

**Description:**  
axios Inefficient Regular Expression Complexity vulnerability

**Recommendation:**  
Review GHSA-cph5-m8f7-6c5x in OSV.dev and upgrade the affected dependency to a patched or currently supported version.

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

## 7. LLM Findings

No LLM-assisted findings were recorded.

---

## 8. Metrics

| Metric | Value |
|---|---:|
| Coverage | 1.0 |
| Confidence | 0.8 |
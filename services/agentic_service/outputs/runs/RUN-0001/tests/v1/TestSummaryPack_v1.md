# Test Summary Pack

**Run ID:** RUN-0001  
**Stage:** testing  
**Version:** v1  
**Generated At:** 2026-05-14T06:38:26.630491+00:00  
**Target Path:** outputs/runs/RUN-0001/code/v1/generated_app

---

## 1. Quality Gate

| Field | Value |
|---|---|
| Status | **FAIL** |
| Reason | 4 test(s) failed. |
| Policy | FAIL if any generated test fails. |

---

## 2. Test Summary

| Metric | Count |
|---|---:|
| Total Tests | 33 |
| Passed | 29 |
| Failed | 4 |
| Skipped | 0 |
| Not Run | 0 |

---

## 3. Metrics

| Metric | Value |
|---|---:|
| Test Coverage | 1.0 |
| Pass Rate | 0.88 |
| Execution Efficiency | 472.0 ms |

---

## 4. Traceability Summary

| Metric | Value |
|---|---:|
| Total Test Cases | 8 |
| Mapped Test Cases | 8 |
| Partially Mapped Test Cases | 0 |
| Unmapped Test Cases | 0 |
| Coverage Percentage | 100.0% |

---

## 5. Dashboard Counts

| Item | Count |
|---|---:|
| Generated Test Files | 8 |
| Test Cases | 8 |
| Execution Results | 33 |
| Regression Test Cases | 5 |
| Security Validation Cases | 4 |
| Failed Results | 4 |

---

## 6. Failed Results

| Test ID | Status | Duration | Message |
|---|---|---:|---|
| outputs/runs/RUN-0001/tests/v1/generated_tests/test_regression_cases.py::test_regression_negative_quantity_is_rejected | failed | 14 ms | Test failed. See pytest stdout/stderr for details. |
| outputs/runs/RUN-0001/tests/v1/generated_tests/test_regression_cases.py::test_regression_missing_payment_or_customer_is_rejected | failed | 14 ms | Test failed. See pytest stdout/stderr for details. |
| outputs/runs/RUN-0001/tests/v1/generated_tests/test_validation_edge_cases.py::test_customer_or_payment_validation_exists | failed | 14 ms | Test failed. See pytest stdout/stderr for details. |
| outputs/runs/RUN-0001/tests/v1/generated_tests/test_validation_edge_cases.py::test_out_of_stock_handling_exists | failed | 14 ms | Test failed. See pytest stdout/stderr for details. |

---

## 7. Recommendations

- Some generated tests failed. Review pytest stdout/stderr in TestReport_v1.json.
- Generated pytest files were executed.
- Functional API-style tests were generated for catalog, cart, checkout, and order.
- Integration workflow tests were generated for Product -> Cart -> Checkout -> Order.
- Validation and edge-case tests were generated for common e-commerce failure cases.
- Regression tests were generated to prevent known bugs from returning.
- Security validation tests were generated using SecurityReport_v1.json.
- Test traceability mapping was added for requirement, API, module, and security validation coverage.
- Testing Summary Pack was generated for dashboard and API integration.

---

## 8. Artifact Paths

| Artifact | Path |
|---|---|
| Test Report JSON | outputs\runs\RUN-0001\tests\v1\TestReport_v1.json |
| Test Report Markdown | outputs\runs\RUN-0001\tests\v1\TestReport_v1.md |
| Test Summary Pack JSON | outputs\runs\RUN-0001\tests\v1\TestSummaryPack_v1.json |
| Test Summary Pack Markdown | outputs\runs\RUN-0001\tests\v1\TestSummaryPack_v1.md |
| Generated Tests Folder | outputs\runs\RUN-0001\tests\v1\generated_tests |
| Regression Tests Folder | outputs\runs\RUN-0001\tests\v1\regression_tests |
| Security Validation Tests Folder | outputs\runs\RUN-0001\tests\v1\security_validation_tests |

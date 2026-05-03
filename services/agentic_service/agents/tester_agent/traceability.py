from typing import List

from agents.tester_agent.schemas import TestCase, TestTraceabilitySummary


class TestTraceabilityMapper:
    """
    Maps generated test cases to requirements, APIs, modules, and security findings.

    This is a rule-based MVP mapper.

    Later, this can be improved using:
    - SRS_v1.json
    - Architecture/APIContract_v1.json
    - SecurityReport_v1.json
    - run_metadata.json
    """

    def map_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """
        Add traceability fields to all test cases.
        """

        for test_case in test_cases:
            self._map_single_test_case(test_case)

        return test_cases

    def summarize_traceability(
        self,
        test_cases: List[TestCase]
    ) -> TestTraceabilitySummary:
        """
        Build traceability summary for the TestReport.
        """

        total = len(test_cases)

        mapped = sum(
            1 for test_case in test_cases
            if test_case.traceability_status == "mapped"
        )

        partial = sum(
            1 for test_case in test_cases
            if test_case.traceability_status == "partial"
        )

        unmapped = sum(
            1 for test_case in test_cases
            if test_case.traceability_status == "unmapped"
        )

        coverage = 0.0

        if total > 0:
            coverage = round((mapped / total) * 100, 2)

        return TestTraceabilitySummary(
            total_test_cases=total,
            mapped_test_cases=mapped,
            partially_mapped_test_cases=partial,
            unmapped_test_cases=unmapped,
            coverage_percentage=coverage
        )

    def _map_single_test_case(self, test_case: TestCase) -> None:
        """
        Apply rule-based mapping for one test case.
        """

        module = test_case.target_module.lower()
        test_type = test_case.test_type.lower()
        title = test_case.title.lower()

        if module == "project":
            test_case.related_requirement_id = "NFR-TEST-001"
            test_case.api_endpoint = "N/A"
            test_case.traceability_status = "mapped"
            return

        if module == "backend":
            test_case.related_requirement_id = "NFR-TEST-002"
            test_case.api_endpoint = "N/A"
            test_case.traceability_status = "mapped"
            return

        if module == "ecommerce":
            test_case.related_requirement_id = "FR-001"
            test_case.api_endpoint = "/products, /cart, /checkout, /orders"
            test_case.traceability_status = "mapped"
            return

        if module == "ecommerce_api":
            test_case.related_requirement_id = "FR-API-001"
            test_case.api_endpoint = "/products, /cart, /checkout, /orders"
            test_case.traceability_status = "mapped"
            return

        if module == "ecommerce_workflow":
            test_case.related_requirement_id = "FR-WORKFLOW-001"
            test_case.api_endpoint = "/products → /cart → /checkout → /orders"
            test_case.traceability_status = "mapped"
            return

        if module == "validation":
            test_case.related_requirement_id = "NFR-VALIDATION-001"
            test_case.api_endpoint = "/products, /cart, /checkout"
            test_case.traceability_status = "mapped"
            return

        if module == "regression":
            test_case.related_requirement_id = "NFR-REGRESSION-001"
            test_case.api_endpoint = "/cart, /checkout, /orders"
            test_case.traceability_status = "mapped"
            return

        if module == "security_validation" or test_type == "security_validation":
            test_case.related_requirement_id = "NFR-SEC-VALIDATION-001"
            test_case.api_endpoint = "SecurityReport_v1.json"
            test_case.related_security_finding_id = "ALL"
            test_case.traceability_status = "mapped"
            return

        if "catalog" in title or "product" in title:
            test_case.related_requirement_id = "FR-001"
            test_case.api_endpoint = "/products"
            test_case.traceability_status = "partial"
            return

        if "cart" in title:
            test_case.related_requirement_id = "FR-002"
            test_case.api_endpoint = "/cart"
            test_case.traceability_status = "partial"
            return

        if "checkout" in title:
            test_case.related_requirement_id = "FR-003"
            test_case.api_endpoint = "/checkout"
            test_case.traceability_status = "partial"
            return

        if "order" in title:
            test_case.related_requirement_id = "FR-004"
            test_case.api_endpoint = "/orders"
            test_case.traceability_status = "partial"
            return

        test_case.traceability_status = "unmapped"
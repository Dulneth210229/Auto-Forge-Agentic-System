import json
from pathlib import Path

from agents.tester_agent.agent import TesterAgent


def test_tester_agent_generates_security_validation_tests(tmp_path: Path):
    """
    Test whether TesterAgent:
    - generates pytest files
    - includes regression tests
    - includes security validation tests
    - validates SecurityReport_v1.json
    - executes individual pytest results
    """

    target = tmp_path / "sample_ecommerce_app"
    target.mkdir()

    app_file = target / "app.py"
    app_file.write_text(
        """
def list_products():
    return [{"id": 1, "name": "Demo Product", "price": 100, "stock": 10}]

def get_products():
    return list_products()

def get_product(product_id):
    if product_id is None:
        return {"error": "missing product id"}
    if product_id <= 0:
        return {"error": "invalid product id"}
    return {"id": product_id, "name": "Demo Product", "price": 100, "stock": 10}

def add_to_cart(product_id, quantity):
    if quantity <= 0:
        return {"error": "invalid quantity, quantity must be positive and greater than 0"}

    cart = []
    cart.append({"product_id": product_id, "quantity": quantity})
    return cart

def view_cart():
    return {"cart": []}

def checkout(cart, customer=None, payment=None):
    if not cart:
        return {"error": "cannot checkout with an empty cart"}
    if customer is None:
        return {"error": "missing customer required"}
    if payment is None:
        return {"error": "missing payment required"}

    return {"order_id": 1, "status": "created", "payment": "mock"}

def process_checkout(cart):
    return checkout(cart, customer={"email": "demo@example.com"}, payment={"method": "mock"})

def create_order(customer_id):
    return {"order_id": 1, "customer_id": customer_id, "status": "created"}

def place_order(customer_id):
    return create_order(customer_id)

def order_history(customer_id):
    return [create_order(customer_id)]

def validate_price(price):
    if price <= 0:
        return {"error": "invalid price"}
    return {"price": price}

def check_stock(product_id, quantity):
    available_quantity = 10
    if quantity > available_quantity:
        return {"error": "insufficient stock / out of stock"}
    return {"status": "in stock"}
""",
        encoding="utf-8"
    )

    output_root = tmp_path / "outputs"

    security_report_dir = output_root / "runs" / "RUN-TEST" / "security" / "v1"
    security_report_dir.mkdir(parents=True, exist_ok=True)

    security_report_path = security_report_dir / "SecurityReport_v1.json"

    security_report = {
        "run_id": "RUN-TEST",
        "stage": "security",
        "version": "v1",
        "summary": {
            "total_findings": 1,
            "critical": 0,
            "high": 1,
            "medium": 0,
            "low": 0
        },
        "findings": [
            {
                "finding_id": "SEC-001",
                "title": "Hardcoded secret detected",
                "description": "A hardcoded API key was found.",
                "severity": "High",
                "file": "sample_ecommerce_app/app.py",
                "line": 10,
                "detection_method": "AST",
                "cwe": "CWE-798",
                "recommendation": "Move secrets to environment variables.",
                "traceability": {
                    "requirement_id": "NFR-SEC-001",
                    "api": "N/A",
                    "module": "security_configuration"
                }
            }
        ],
        "dependency_vulnerabilities": [],
        "llm_findings": [],
        "security_gate": {
            "status": "WARN",
            "reason": "Security gate warning because High severity findings exist.",
            "policy": "WARN if High findings exist but are within threshold.",
            "blocking_findings": ["SEC-001"]
        },
        "fix_suggestions": [
            {
                "finding_id": "SEC-001",
                "issue": "Hardcoded secret detected",
                "severity": "High",
                "file": "sample_ecommerce_app/app.py",
                "recommended_fix": "Move hardcoded secrets into environment variables.",
                "example_fix": "SECRET_KEY = os.getenv('SECRET_KEY')",
                "priority": "High",
                "effort": "Low"
            }
        ],
        "metrics": {
            "coverage": 1.0,
            "confidence": 0.8
        }
    }

    security_report_path.write_text(
        json.dumps(security_report, indent=2),
        encoding="utf-8"
    )

    agent = TesterAgent(output_root=str(output_root))

    result = agent.run(
        run_id="RUN-TEST",
        version="v1",
        target_path=str(target)
    )

    assert result["run_id"] == "RUN-TEST"
    assert result["stage"] == "testing"
    assert result["version"] == "v1"

    assert result["generated_tests_path"].endswith("generated_tests")
    assert result["generated_test_files_count"] == 8

    assert result["pytest_status"] == "passed"
    assert result["pytest_exit_code"] == 0

    assert result["summary"]["total_tests"] >= 33
    assert result["summary"]["passed"] >= 33
    assert result["summary"]["failed"] == 0
    assert result["summary"]["not_run"] == 0

    assert result["json_path"].endswith("TestReport_v1.json")
    assert result["markdown_path"].endswith("TestReport_v1.md")
    assert result["metadata_path"].endswith("run_metadata.json")

    assert Path(result["json_path"]).exists()
    assert Path(result["markdown_path"]).exists()
    assert Path(result["metadata_path"]).exists()

    generated_tests_path = Path(result["generated_tests_path"])
    regression_tests_path = output_root / "runs" / "RUN-TEST" / "tests" / "v1" / "regression_tests"
    security_validation_tests_path = output_root / "runs" / "RUN-TEST" / "tests" / "v1" / "security_validation_tests"

    assert (generated_tests_path / "test_project_structure.py").exists()
    assert (generated_tests_path / "test_python_syntax.py").exists()
    assert (generated_tests_path / "test_ecommerce_keywords.py").exists()
    assert (generated_tests_path / "test_functional_api_contract.py").exists()
    assert (generated_tests_path / "test_ecommerce_workflow.py").exists()
    assert (generated_tests_path / "test_validation_edge_cases.py").exists()
    assert (generated_tests_path / "test_regression_cases.py").exists()
    assert (generated_tests_path / "test_security_validation.py").exists()

    assert regression_tests_path.exists()
    assert (regression_tests_path / "regression_cases.json").exists()

    assert security_validation_tests_path.exists()
    assert (security_validation_tests_path / "security_validation_cases.json").exists()
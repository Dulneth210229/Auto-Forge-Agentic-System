from pathlib import Path

from agents.tester_agent.agent import TesterAgent


def test_tester_agent_generates_regression_tests(tmp_path: Path):
    """
    Test whether TesterAgent:
    - generates pytest files
    - includes functional API contract tests
    - includes integration workflow tests
    - includes validation and edge-case tests
    - includes regression tests
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
    assert result["generated_test_files_count"] == 7

    assert result["pytest_status"] == "passed"
    assert result["pytest_exit_code"] == 0

    assert result["summary"]["total_tests"] >= 26
    assert result["summary"]["passed"] >= 26
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

    assert (generated_tests_path / "test_project_structure.py").exists()
    assert (generated_tests_path / "test_python_syntax.py").exists()
    assert (generated_tests_path / "test_ecommerce_keywords.py").exists()
    assert (generated_tests_path / "test_functional_api_contract.py").exists()
    assert (generated_tests_path / "test_ecommerce_workflow.py").exists()
    assert (generated_tests_path / "test_validation_edge_cases.py").exists()
    assert (generated_tests_path / "test_regression_cases.py").exists()

    assert regression_tests_path.exists()
    assert (regression_tests_path / "regression_cases.json").exists()
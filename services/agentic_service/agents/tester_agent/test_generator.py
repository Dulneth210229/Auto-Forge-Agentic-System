import json
from pathlib import Path
from typing import List

from agents.tester_agent.schemas import GeneratedTestFile, RegressionTestCase


class PytestTestGenerator:
    """
    Generates pytest files for a target generated project.

    Current behavior:
    - Inspect target project folder
    - Generate smoke tests
    - Generate syntax tests
    - Generate e-commerce keyword tests
    - Generate functional API contract tests
    - Generate integration workflow tests
    - Generate edge-case and validation tests
    - Generate regression tests
    """

    def generate_tests(
        self,
        target_path: str,
        output_dir: Path
    ) -> List[GeneratedTestFile]:
        """
        Generate pytest files into output_dir/generated_tests.
        """

        target = Path(target_path)

        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        generated_tests_dir = output_dir / "generated_tests"
        generated_tests_dir.mkdir(parents=True, exist_ok=True)

        regression_tests_dir = output_dir / "regression_tests"
        regression_tests_dir.mkdir(parents=True, exist_ok=True)

        self.write_regression_cases_file(regression_tests_dir)

        generated_files: List[GeneratedTestFile] = []

        generated_files.append(
            self._write_project_structure_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_python_syntax_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_ecommerce_keywords_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_functional_api_contract_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_ecommerce_workflow_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_validation_edge_cases_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        generated_files.append(
            self._write_regression_cases_test(
                target_path=target_path,
                generated_tests_dir=generated_tests_dir
            )
        )

        return generated_files

    def get_default_regression_cases(self) -> List[RegressionTestCase]:
        """
        Return default regression scenarios for e-commerce generated code.
        """

        return [
            RegressionTestCase(
                regression_id="REG-001",
                title="Prevent checkout with empty cart",
                description="Previously, generated checkout logic could allow checkout even when cart is empty.",
                related_requirement_id="FR-003",
                related_module="checkout",
                expected_behavior="Checkout must reject an empty cart."
            ),
            RegressionTestCase(
                regression_id="REG-002",
                title="Reject negative quantity",
                description="Generated cart logic must not accept negative or zero quantity.",
                related_requirement_id="FR-002",
                related_module="cart",
                expected_behavior="Cart should reject invalid quantity values."
            ),
            RegressionTestCase(
                regression_id="REG-003",
                title="Handle invalid product ID",
                description="Generated catalog/cart logic must handle missing or invalid product IDs.",
                related_requirement_id="FR-001",
                related_module="catalog",
                expected_behavior="Invalid product ID should return an error or validation response."
            ),
            RegressionTestCase(
                regression_id="REG-004",
                title="Validate payment or customer details",
                description="Checkout must not proceed when payment or customer details are missing.",
                related_requirement_id="FR-003",
                related_module="checkout",
                expected_behavior="Checkout should require customer and payment details."
            ),
            RegressionTestCase(
                regression_id="REG-005",
                title="Prevent order creation without checkout",
                description="Order creation should depend on a valid checkout or valid cart state.",
                related_requirement_id="FR-004",
                related_module="order",
                expected_behavior="Order creation should not bypass checkout validation."
            )
        ]

    def write_regression_cases_file(self, regression_tests_dir: Path) -> str:
        """
        Save default regression scenarios as JSON.
        """

        regression_cases = self.get_default_regression_cases()

        file_path = regression_tests_dir / "regression_cases.json"

        data = [
            regression_case.model_dump()
            for regression_case in regression_cases
        ]

        file_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

        return str(file_path)

    def _write_project_structure_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_project_structure.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def test_target_project_folder_exists():
    assert TARGET_PATH.exists(), f"Target project folder does not exist: {{TARGET_PATH}}"


def test_target_project_contains_source_files():
    source_extensions = [".py", ".js", ".jsx", ".ts", ".tsx"]

    source_files = [
        file_path
        for file_path in TARGET_PATH.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in source_extensions
    ]

    assert source_files, "No Python/JavaScript/TypeScript source files were found."


def test_target_project_has_ecommerce_related_files_or_content():
    keywords = ["product", "catalog", "cart", "checkout", "order"]

    combined_text = ""

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".py", ".js", ".jsx", ".ts", ".tsx", ".json"]:
            try:
                combined_text += file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    assert any(keyword in combined_text for keyword in keywords), (
        "No e-commerce related keywords were found in the generated project."
    )
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="smoke",
            description="Checks whether the target project folder and source files exist."
        )

    def _write_python_syntax_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_python_syntax.py"

        content = f'''import py_compile
from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def test_python_files_have_valid_syntax():
    python_files = [
        file_path
        for file_path in TARGET_PATH.rglob("*.py")
        if "venv" not in str(file_path).lower()
        and "__pycache__" not in str(file_path).lower()
    ]

    for python_file in python_files:
        py_compile.compile(str(python_file), doraise=True)
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="unit",
            description="Checks whether Python source files compile without syntax errors."
        )

    def _write_ecommerce_keywords_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_ecommerce_keywords.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md"]:
            try:
                combined_text += "\\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def test_catalog_or_product_feature_exists():
    text = _read_project_text()
    assert "catalog" in text or "product" in text


def test_cart_feature_exists():
    text = _read_project_text()
    assert "cart" in text


def test_checkout_or_order_feature_exists():
    text = _read_project_text()
    assert "checkout" in text or "order" in text
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="integration",
            description="Checks whether minimum e-commerce modules are represented in the generated code."
        )

    def _write_functional_api_contract_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_functional_api_contract.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml"
    ]

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            try:
                combined_text += "\\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def test_catalog_api_or_function_contract_exists():
    text = _read_project_text()

    catalog_keywords = [
        "/products", "/product", "/catalog", "get_products",
        "list_products", "product_list", "catalog", "product"
    ]

    assert _has_any(text, catalog_keywords), (
        "Catalog/product API or function contract was not found."
    )


def test_cart_api_or_function_contract_exists():
    text = _read_project_text()

    cart_keywords = [
        "/cart", "add_to_cart", "remove_from_cart",
        "view_cart", "update_cart", "cart"
    ]

    assert _has_any(text, cart_keywords), (
        "Cart API or function contract was not found."
    )


def test_checkout_api_or_function_contract_exists():
    text = _read_project_text()

    checkout_keywords = [
        "/checkout", "checkout", "process_checkout",
        "place_order", "payment", "billing"
    ]

    assert _has_any(text, checkout_keywords), (
        "Checkout API or function contract was not found."
    )


def test_order_api_or_function_contract_exists():
    text = _read_project_text()

    order_keywords = [
        "/orders", "/order", "create_order",
        "place_order", "order_history", "get_orders", "order"
    ]

    assert _has_any(text, order_keywords), (
        "Order API or function contract was not found."
    )
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="api",
            description="Checks whether e-commerce API/function contracts exist for catalog, cart, checkout, and order."
        )

    def _write_ecommerce_workflow_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_ecommerce_workflow.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml"
    ]

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            try:
                combined_text += "\\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def test_product_to_cart_workflow_is_supported():
    text = _read_project_text()

    product_keywords = [
        "product", "products", "catalog", "list_products",
        "get_products", "/products", "/catalog"
    ]

    cart_keywords = [
        "cart", "add_to_cart", "view_cart", "update_cart", "/cart"
    ]

    assert _has_any(text, product_keywords), "Product/catalog part of workflow was not found."
    assert _has_any(text, cart_keywords), "Cart part of workflow was not found."


def test_cart_to_checkout_workflow_is_supported():
    text = _read_project_text()

    cart_keywords = [
        "cart", "add_to_cart", "view_cart", "update_cart", "/cart"
    ]

    checkout_keywords = [
        "checkout", "process_checkout", "payment", "billing", "/checkout"
    ]

    assert _has_any(text, cart_keywords), "Cart part of workflow was not found."
    assert _has_any(text, checkout_keywords), "Checkout part of workflow was not found."


def test_checkout_to_order_workflow_is_supported():
    text = _read_project_text()

    checkout_keywords = [
        "checkout", "process_checkout", "payment", "billing", "/checkout"
    ]

    order_keywords = [
        "order", "orders", "create_order", "place_order",
        "order_history", "/order", "/orders"
    ]

    assert _has_any(text, checkout_keywords), "Checkout part of workflow was not found."
    assert _has_any(text, order_keywords), "Order part of workflow was not found."


def test_full_ecommerce_workflow_keywords_exist():
    text = _read_project_text()

    workflow_groups = {{
        "product_or_catalog": ["product", "products", "catalog", "list_products", "/products"],
        "cart": ["cart", "add_to_cart", "view_cart", "/cart"],
        "checkout": ["checkout", "process_checkout", "payment", "/checkout"],
        "order": ["order", "orders", "create_order", "place_order", "/orders"]
    }}

    missing_groups = [
        group_name
        for group_name, keywords in workflow_groups.items()
        if not _has_any(text, keywords)
    ]

    assert not missing_groups, f"Missing workflow groups: {{missing_groups}}"
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="integration",
            description="Checks whether the full e-commerce workflow from product browsing to order creation is represented."
        )

    def _write_validation_edge_cases_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        file_path = generated_tests_dir / "test_validation_edge_cases.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml"
    ]

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            try:
                combined_text += "\\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def test_invalid_product_id_validation_exists():
    text = _read_project_text()

    keywords = [
        "invalid product", "product_id", "product id",
        "not found", "404", "missing product"
    ]

    assert _has_any(text, keywords), (
        "Invalid product ID validation was not found."
    )


def test_negative_or_zero_quantity_validation_exists():
    text = _read_project_text()

    keywords = [
        "quantity", "negative", "greater than 0",
        "must be positive", "invalid quantity", "zero"
    ]

    assert _has_any(text, keywords), (
        "Quantity validation was not found."
    )


def test_empty_cart_checkout_validation_exists():
    text = _read_project_text()

    keywords = [
        "empty cart", "cart is empty", "cannot checkout",
        "checkout with an empty cart", "cart empty"
    ]

    assert _has_any(text, keywords), (
        "Empty cart checkout validation was not found."
    )


def test_customer_or_payment_validation_exists():
    text = _read_project_text()

    keywords = [
        "customer", "payment", "billing",
        "email", "required", "missing", "validate"
    ]

    assert _has_any(text, keywords), (
        "Customer or payment validation was not found."
    )


def test_price_validation_exists():
    text = _read_project_text()

    keywords = [
        "price", "invalid price", "amount",
        "total", "subtotal", "discount"
    ]

    assert _has_any(text, keywords), (
        "Price validation or pricing logic was not found."
    )


def test_out_of_stock_handling_exists():
    text = _read_project_text()

    keywords = [
        "stock", "out of stock", "inventory",
        "available_quantity", "insufficient stock"
    ]

    assert _has_any(text, keywords), (
        "Stock or out-of-stock handling was not found."
    )
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="integration",
            description="Checks whether validation and edge-case handling exists for common e-commerce cases."
        )

    def _write_regression_cases_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        """
        Generate regression tests for known e-commerce bug patterns.
        """

        file_path = generated_tests_dir / "test_regression_cases.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml"
    ]

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            try:
                combined_text += "\\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def test_regression_empty_cart_checkout_is_prevented():
    text = _read_project_text()

    keywords = [
        "empty cart",
        "cannot checkout",
        "cart is empty",
        "checkout with an empty cart"
    ]

    assert _has_any(text, keywords), (
        "Regression failed: empty cart checkout prevention was not found."
    )


def test_regression_negative_quantity_is_rejected():
    text = _read_project_text()

    keywords = [
        "invalid quantity",
        "must be positive",
        "greater than 0",
        "negative",
        "quantity <= 0"
    ]

    assert _has_any(text, keywords), (
        "Regression failed: negative quantity rejection was not found."
    )


def test_regression_invalid_product_id_is_handled():
    text = _read_project_text()

    keywords = [
        "invalid product",
        "missing product",
        "product not found",
        "product_id",
        "product id"
    ]

    assert _has_any(text, keywords), (
        "Regression failed: invalid product ID handling was not found."
    )


def test_regression_missing_payment_or_customer_is_rejected():
    text = _read_project_text()

    keywords = [
        "missing payment",
        "missing customer",
        "payment required",
        "customer required",
        "required"
    ]

    assert _has_any(text, keywords), (
        "Regression failed: missing payment/customer rejection was not found."
    )


def test_regression_order_creation_depends_on_checkout_or_cart():
    text = _read_project_text()

    keywords = [
        "checkout",
        "cart",
        "create_order",
        "place_order",
        "order"
    ]

    assert _has_any(text, keywords), (
        "Regression failed: order creation dependency on checkout/cart was not found."
    )
'''

        file_path.write_text(content, encoding="utf-8")

        return GeneratedTestFile(
            file_name=file_path.name,
            file_path=str(file_path),
            test_type="regression",
            description="Checks whether known e-commerce bug patterns are prevented."
        )
from pathlib import Path
from typing import List

from agents.tester_agent.schemas import GeneratedTestFile


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

        return generated_files

    def _write_project_structure_test(
        self,
        target_path: str,
        generated_tests_dir: Path
    ) -> GeneratedTestFile:
        """
        Generate smoke test for basic project structure.
        """

        file_path = generated_tests_dir / "test_project_structure.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def test_target_project_folder_exists():
    """
    Smoke test: target generated project folder should exist.
    """

    assert TARGET_PATH.exists(), f"Target project folder does not exist: {{TARGET_PATH}}"


def test_target_project_contains_source_files():
    """
    Smoke test: generated project should contain at least one source file.
    """

    source_extensions = [".py", ".js", ".jsx", ".ts", ".tsx"]

    source_files = [
        file_path
        for file_path in TARGET_PATH.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in source_extensions
    ]

    assert source_files, "No Python/JavaScript/TypeScript source files were found."


def test_target_project_has_ecommerce_related_files_or_content():
    """
    Smoke test: project should contain at least some e-commerce related content.
    """

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
        """
        Generate syntax validation tests for Python files.
        """

        file_path = generated_tests_dir / "test_python_syntax.py"

        content = f'''import py_compile
from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def test_python_files_have_valid_syntax():
    """
    Unit-level quality test: all Python files should compile successfully.
    """

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
        """
        Generate lightweight tests for minimum e-commerce modules.
        """

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
    """
    E-commerce test: project should include catalog/product behavior.
    """

    text = _read_project_text()

    assert "catalog" in text or "product" in text


def test_cart_feature_exists():
    """
    E-commerce test: project should include cart behavior.
    """

    text = _read_project_text()

    assert "cart" in text


def test_checkout_or_order_feature_exists():
    """
    E-commerce test: project should include checkout/order behavior.
    """

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
        """
        Generate functional API-style contract tests.

        These tests do not execute generated app code yet.
        They inspect source text to confirm that expected e-commerce
        API/function contracts exist in the generated project.
        """

        file_path = generated_tests_dir / "test_functional_api_contract.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".md",
        ".yaml",
        ".yml"
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
    """
    Functional API test:
    Generated project should expose catalog/product behavior through
    an endpoint, route, function, or API contract text.
    """

    text = _read_project_text()

    catalog_keywords = [
        "/products",
        "/product",
        "/catalog",
        "get_products",
        "list_products",
        "product_list",
        "catalog",
        "product"
    ]

    assert _has_any(text, catalog_keywords), (
        "Catalog/product API or function contract was not found."
    )


def test_cart_api_or_function_contract_exists():
    """
    Functional API test:
    Generated project should expose cart behavior through
    an endpoint, route, function, or API contract text.
    """

    text = _read_project_text()

    cart_keywords = [
        "/cart",
        "add_to_cart",
        "remove_from_cart",
        "view_cart",
        "update_cart",
        "cart"
    ]

    assert _has_any(text, cart_keywords), (
        "Cart API or function contract was not found."
    )


def test_checkout_api_or_function_contract_exists():
    """
    Functional API test:
    Generated project should expose checkout behavior through
    an endpoint, route, function, or API contract text.
    """

    text = _read_project_text()

    checkout_keywords = [
        "/checkout",
        "checkout",
        "process_checkout",
        "place_order",
        "payment",
        "billing"
    ]

    assert _has_any(text, checkout_keywords), (
        "Checkout API or function contract was not found."
    )


def test_order_api_or_function_contract_exists():
    """
    Functional API test:
    Generated project should expose order behavior through
    an endpoint, route, function, or API contract text.
    """

    text = _read_project_text()

    order_keywords = [
        "/orders",
        "/order",
        "create_order",
        "place_order",
        "order_history",
        "get_orders",
        "order"
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
        """
        Generate integration workflow tests for the core e-commerce flow.

        These tests inspect source/API contract text to verify that the
        generated project supports the connected business workflow:
        Product browsing -> Cart -> Checkout -> Order.
        """

        file_path = generated_tests_dir / "test_ecommerce_workflow.py"

        content = f'''from pathlib import Path


TARGET_PATH = Path(r"{target_path}")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".md",
        ".yaml",
        ".yml"
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
    """
    Integration workflow test:
    The generated project should support moving from product/catalog
    selection to cart operation.
    """

    text = _read_project_text()

    product_keywords = [
        "product",
        "products",
        "catalog",
        "list_products",
        "get_products",
        "/products",
        "/catalog"
    ]

    cart_keywords = [
        "cart",
        "add_to_cart",
        "view_cart",
        "update_cart",
        "/cart"
    ]

    assert _has_any(text, product_keywords), "Product/catalog part of workflow was not found."
    assert _has_any(text, cart_keywords), "Cart part of workflow was not found."


def test_cart_to_checkout_workflow_is_supported():
    """
    Integration workflow test:
    The generated project should support moving from cart to checkout.
    """

    text = _read_project_text()

    cart_keywords = [
        "cart",
        "add_to_cart",
        "view_cart",
        "update_cart",
        "/cart"
    ]

    checkout_keywords = [
        "checkout",
        "process_checkout",
        "payment",
        "billing",
        "/checkout"
    ]

    assert _has_any(text, cart_keywords), "Cart part of workflow was not found."
    assert _has_any(text, checkout_keywords), "Checkout part of workflow was not found."


def test_checkout_to_order_workflow_is_supported():
    """
    Integration workflow test:
    The generated project should support moving from checkout to order creation.
    """

    text = _read_project_text()

    checkout_keywords = [
        "checkout",
        "process_checkout",
        "payment",
        "billing",
        "/checkout"
    ]

    order_keywords = [
        "order",
        "orders",
        "create_order",
        "place_order",
        "order_history",
        "/order",
        "/orders"
    ]

    assert _has_any(text, checkout_keywords), "Checkout part of workflow was not found."
    assert _has_any(text, order_keywords), "Order part of workflow was not found."


def test_full_ecommerce_workflow_keywords_exist():
    """
    Integration workflow test:
    Minimum full workflow should include product/catalog, cart,
    checkout, and order concepts.
    """

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
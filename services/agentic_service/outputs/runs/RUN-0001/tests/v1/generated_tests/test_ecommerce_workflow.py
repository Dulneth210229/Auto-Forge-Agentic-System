from pathlib import Path


TARGET_PATH = Path(r"./sample_ecommerce_app")


def _read_project_text() -> str:
    combined_text = ""

    allowed_extensions = [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml"
    ]

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            try:
                combined_text += "\n" + file_path.read_text(encoding="utf-8").lower()
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

    workflow_groups = {
        "product_or_catalog": ["product", "products", "catalog", "list_products", "/products"],
        "cart": ["cart", "add_to_cart", "view_cart", "/cart"],
        "checkout": ["checkout", "process_checkout", "payment", "/checkout"],
        "order": ["order", "orders", "create_order", "place_order", "/orders"]
    }

    missing_groups = [
        group_name
        for group_name, keywords in workflow_groups.items()
        if not _has_any(text, keywords)
    ]

    assert not missing_groups, f"Missing workflow groups: {missing_groups}"

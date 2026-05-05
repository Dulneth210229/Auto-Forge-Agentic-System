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

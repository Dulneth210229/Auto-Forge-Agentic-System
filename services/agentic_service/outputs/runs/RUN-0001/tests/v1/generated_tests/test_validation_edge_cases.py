from pathlib import Path


TARGET_PATH = Path(r"./sample_ecommerce_app")


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
                combined_text += "\n" + file_path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

    return combined_text


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def test_invalid_product_id_validation_exists():
    """
    Validation test:
    Project should include handling for invalid or missing product IDs.
    """

    text = _read_project_text()

    keywords = [
        "invalid product",
        "product_id",
        "product id",
        "not found",
        "404",
        "missing product"
    ]

    assert _has_any(text, keywords), (
        "Invalid product ID validation was not found."
    )


def test_negative_or_zero_quantity_validation_exists():
    """
    Validation test:
    Project should include handling for negative or zero cart quantities.
    """

    text = _read_project_text()

    keywords = [
        "quantity",
        "negative",
        "greater than 0",
        "must be positive",
        "invalid quantity",
        "zero"
    ]

    assert _has_any(text, keywords), (
        "Quantity validation was not found."
    )


def test_empty_cart_checkout_validation_exists():
    """
    Validation test:
    Project should prevent checkout with an empty cart.
    """

    text = _read_project_text()

    keywords = [
        "empty cart",
        "cart is empty",
        "cannot checkout",
        "checkout with an empty cart",
        "cart empty"
    ]

    assert _has_any(text, keywords), (
        "Empty cart checkout validation was not found."
    )


def test_customer_or_payment_validation_exists():
    """
    Validation test:
    Project should include customer/payment input validation.
    """

    text = _read_project_text()

    keywords = [
        "customer",
        "payment",
        "billing",
        "email",
        "required",
        "missing",
        "validate"
    ]

    assert _has_any(text, keywords), (
        "Customer or payment validation was not found."
    )


def test_price_validation_exists():
    """
    Validation test:
    Project should include price validation or pricing rules.
    """

    text = _read_project_text()

    keywords = [
        "price",
        "invalid price",
        "amount",
        "total",
        "subtotal",
        "discount"
    ]

    assert _has_any(text, keywords), (
        "Price validation or pricing logic was not found."
    )


def test_out_of_stock_handling_exists():
    """
    Validation test:
    Project should include stock or out-of-stock handling.
    """

    text = _read_project_text()

    keywords = [
        "stock",
        "out of stock",
        "inventory",
        "available_quantity",
        "insufficient stock"
    ]

    assert _has_any(text, keywords), (
        "Stock or out-of-stock handling was not found."
    )

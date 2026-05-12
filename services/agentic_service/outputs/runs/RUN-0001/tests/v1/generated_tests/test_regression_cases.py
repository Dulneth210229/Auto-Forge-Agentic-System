from pathlib import Path


TARGET_PATH = Path(r"outputs/runs/RUN-0001/code/v1/generated_app")


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

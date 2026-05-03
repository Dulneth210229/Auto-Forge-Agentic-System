from pathlib import Path


TARGET_PATH = Path(r"./sample_ecommerce_app")


def _read_project_text() -> str:
    combined_text = ""

    for file_path in TARGET_PATH.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md"]:
            try:
                combined_text += "\n" + file_path.read_text(encoding="utf-8").lower()
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

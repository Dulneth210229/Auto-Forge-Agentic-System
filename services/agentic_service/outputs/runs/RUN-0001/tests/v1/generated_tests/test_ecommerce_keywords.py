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


def test_catalog_or_product_feature_exists():
    text = _read_project_text()
    assert "catalog" in text or "product" in text


def test_cart_feature_exists():
    text = _read_project_text()
    assert "cart" in text


def test_checkout_or_order_feature_exists():
    text = _read_project_text()
    assert "checkout" in text or "order" in text

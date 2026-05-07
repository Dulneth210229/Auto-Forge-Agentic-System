from agents.uiux_agent.flow_builder import build_default_screens, build_user_flow, build_mermaid_from_flow
from agents.uiux_agent.wireframe_builder import fallback_wireframe_html


def test_uiux_flow_generation():
    srs = {
        "project_name": "AutoForge Shop",
        "roles": ["Customer", "Admin"],
        "functional_requirements": [
            {"id": "FR-001", "title": "Browse products", "description": "Customer can browse product catalog."},
            {"id": "FR-002", "title": "Cart", "description": "Customer can add products to cart."},
        ],
    }

    api_contract = {
        "paths": {
            "/products": {},
            "/cart": {},
        }
    }

    screens = build_default_screens(srs, api_contract)
    flow = build_user_flow(screens)
    mermaid = build_mermaid_from_flow(flow)

    assert "flowchart TD" in mermaid
    assert "UI-SCR-02" in mermaid


def test_wireframe_html_generation():
    srs = {
        "project_name": "AutoForge Shop",
        "roles": ["Customer"],
        "functional_requirements": [
            {"id": "FR-001", "title": "Browse products", "description": "Customer can browse products."}
        ],
    }

    screens = build_default_screens(srs, {"paths": {}})
    html = fallback_wireframe_html("AutoForge Shop", screens[0])

    assert "<!DOCTYPE html>" in html
    assert "tailwindcss" in html.lower()
    assert "</html>" in html
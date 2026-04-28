from agents.requirement_agent.schemas import IntakeInput, SRS


def test_intake_schema_validation():
    data = {
        "project_name": "AutoForge Shop",
        "business_goal": "Build an E-commerce platform for online product sales.",
        "target_users": ["Customer", "Admin"],
        "stakeholders": [
            {
                "role": "Business Analyst",
                "description": "Provides and approves requirements."
            }
        ]
    }

    intake = IntakeInput.model_validate(data)

    assert intake.project_name == "AutoForge Shop"
    assert "checkout" in intake.ecommerce_features


def test_srs_schema_validation():
    data = {
        "project_name": "AutoForge Shop",
        "version": "v1",
        "domain": "E-commerce",
        "purpose": "Define requirements for an E-commerce platform.",
        "scope_in": ["Product browsing", "Cart", "Checkout"],
        "scope_out": ["Real payment gateway"],
        "roles": ["Customer", "Admin"],
        "stakeholders": [],
        "workflows": ["Browse catalog", "Add to cart", "Checkout"],
        "business_rules": ["Only in-stock products can be ordered."],
        "constraints": ["Must run locally."],
        "assumptions": ["Payment is mocked."],
        "functional_requirements": [
            {
                "id": "FR-001",
                "title": "Browse products",
                "description": "Customers can browse available products.",
                "priority": "Must",
                "acceptance_criteria": [
                    {
                        "id": "AC-001",
                        "description": "Product list is visible to customers."
                    }
                ]
            }
        ],
        "non_functional_requirements": [
            {
                "id": "NFR-001",
                "category": "Performance",
                "description": "The system should load product pages quickly.",
                "acceptance_criteria": [
                    {
                        "id": "AC-002",
                        "description": "Product listing loads within 3 seconds."
                    }
                ]
            }
        ],
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Browse catalog",
                "actor": "Customer",
                "preconditions": ["Customer opens the website."],
                "main_flow": ["Customer views product catalog."],
                "alternative_flows": ["No products available."],
                "related_requirements": ["FR-001"]
            }
        ]
    }

    srs = SRS.model_validate(data)

    assert srs.functional_requirements[0].id == "FR-001"
    assert srs.non_functional_requirements[0].id == "NFR-001"
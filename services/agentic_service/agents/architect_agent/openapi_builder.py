from typing import List
import yaml

from agents.architect_agent.schemas import APIEndpoint


def build_default_api_endpoints(functional_requirements: list[dict]) -> List[APIEndpoint]:
    """
    Creates a stable API contract for the E-commerce MVP.

    We attach related FR IDs where possible. This gives traceability from
    requirements to API endpoints.
    """

    fr_ids = [fr.get("id", "") for fr in functional_requirements]

    def related(*keywords: str) -> list[str]:
        """
        Finds FR IDs whose title/description contain one of the given keywords.
        If no match is found, return all FR IDs as a safe fallback.
        """
        matched = []

        for fr in functional_requirements:
            text = f"{fr.get('title', '')} {fr.get('description', '')}".lower()
            if any(keyword.lower() in text for keyword in keywords):
                matched.append(fr.get("id", ""))

        return matched or fr_ids[:1]

    return [
        APIEndpoint(
            id="API-001",
            tag="Identity",
            method="POST",
            path="/auth/register",
            summary="Register user",
            description="Creates a new customer account.",
            request_schema="RegisterRequest",
            response_schema="AuthResponse",
            related_requirements=related("register", "account", "user"),
        ),
        APIEndpoint(
            id="API-002",
            tag="Identity",
            method="POST",
            path="/auth/login",
            summary="Login user",
            description="Authenticates a user and returns an access token.",
            request_schema="LoginRequest",
            response_schema="AuthResponse",
            related_requirements=related("login", "authenticate", "user"),
        ),
        APIEndpoint(
            id="API-003",
            tag="Catalog",
            method="GET",
            path="/products",
            summary="List products",
            description="Returns available products for catalog browsing.",
            response_schema="ProductListResponse",
            related_requirements=related("catalog", "browse", "product"),
        ),
        APIEndpoint(
            id="API-004",
            tag="Catalog",
            method="GET",
            path="/products/{product_id}",
            summary="Get product details",
            description="Returns detailed information for a selected product.",
            response_schema="ProductResponse",
            related_requirements=related("product details", "product"),
        ),
        APIEndpoint(
            id="API-005",
            tag="Cart",
            method="GET",
            path="/cart",
            summary="Get cart",
            description="Returns the current user's cart.",
            response_schema="CartResponse",
            related_requirements=related("cart"),
        ),
        APIEndpoint(
            id="API-006",
            tag="Cart",
            method="POST",
            path="/cart/items",
            summary="Add item to cart",
            description="Adds a selected product to the cart.",
            request_schema="AddCartItemRequest",
            response_schema="CartResponse",
            related_requirements=related("cart", "add"),
        ),
        APIEndpoint(
            id="API-007",
            tag="Cart",
            method="PUT",
            path="/cart/items/{item_id}",
            summary="Update cart item",
            description="Updates item quantity in the cart.",
            request_schema="UpdateCartItemRequest",
            response_schema="CartResponse",
            related_requirements=related("cart", "quantity", "update"),
        ),
        APIEndpoint(
            id="API-008",
            tag="Cart",
            method="DELETE",
            path="/cart/items/{item_id}",
            summary="Remove cart item",
            description="Removes a product item from the cart.",
            response_schema="CartResponse",
            related_requirements=related("cart", "remove"),
        ),
        APIEndpoint(
            id="API-009",
            tag="Checkout",
            method="POST",
            path="/checkout",
            summary="Checkout cart",
            description="Validates cart, calculates total, and prepares order placement.",
            request_schema="CheckoutRequest",
            response_schema="CheckoutResponse",
            related_requirements=related("checkout"),
        ),
        APIEndpoint(
            id="API-010",
            tag="Order",
            method="POST",
            path="/orders",
            summary="Place order",
            description="Creates an order from checkout data.",
            request_schema="CreateOrderRequest",
            response_schema="OrderResponse",
            related_requirements=related("order", "place"),
        ),
        APIEndpoint(
            id="API-011",
            tag="Order",
            method="GET",
            path="/orders",
            summary="List order history",
            description="Returns order history for the authenticated customer.",
            response_schema="OrderListResponse",
            related_requirements=related("history", "orders"),
        ),
        APIEndpoint(
            id="API-012",
            tag="Admin",
            method="POST",
            path="/admin/products",
            summary="Create product",
            description="Allows admin to create a product.",
            request_schema="ProductCreateRequest",
            response_schema="ProductResponse",
            related_requirements=related("admin", "product management"),
        ),
    ]


def build_openapi_document(project_name: str, api_endpoints: List[APIEndpoint]) -> dict:
    """
    Converts internal APIEndpoint objects into an OpenAPI 3.0 document.
    """

    paths = {}

    
    for endpoint in api_endpoints:
        method = endpoint.method.lower()

        if endpoint.path not in paths:
            paths[endpoint.path] = {}

        operation = {
            "tags": [endpoint.tag],
            "summary": endpoint.summary,
            "description": f"{endpoint.description}\n\nRelated requirements: {', '.join(endpoint.related_requirements)}",
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{endpoint.response_schema}"
                            }
                        }
                    },
                },
                "400": {"description": "Invalid request"},
                "401": {"description": "Unauthorized"},
                "500": {"description": "Internal server error"},
            },
        }

        # OpenAPI requires every path variable like {product_id}
        # to be explicitly defined as a path parameter.
        path_parameters = []

        if "{product_id}" in endpoint.path:
            path_parameters.append({
                "name": "product_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": "Unique product identifier."
            })

        if "{item_id}" in endpoint.path:
            path_parameters.append({
                "name": "item_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": "Unique cart item identifier."
            })

        if "{order_id}" in endpoint.path:
            path_parameters.append({
                "name": "order_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": "Unique order identifier."
            })

        if path_parameters:
            operation["parameters"] = path_parameters

        if endpoint.request_schema:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{endpoint.request_schema}"
                        }
                    }
                },
            }

        paths[endpoint.path][method] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{project_name} API",
            "version": "1.0.0",
            "description": "Generated OpenAPI contract by AutoForge Architect Agent.",
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Local development server",
            }
        ],
        "paths": paths,
        "components": {
            "schemas": {
                "RegisterRequest": {
                    "type": "object",
                    "required": ["name", "email", "password"],
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
                "LoginRequest": {
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
                "AuthResponse": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "token_type": {"type": "string"},
                    },
                },
                "ProductCreateRequest": {
                    "type": "object",
                    "required": ["name", "price", "stock_quantity"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "price": {"type": "number"},
                        "stock_quantity": {"type": "integer"},
                    },
                },
                "ProductResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "stock_quantity": {"type": "integer"},
                    },
                },
                "ProductListResponse": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ProductResponse"},
                        }
                    },
                },
                "AddCartItemRequest": {
                    "type": "object",
                    "required": ["product_id", "quantity"],
                    "properties": {
                        "product_id": {"type": "string"},
                        "quantity": {"type": "integer"},
                    },
                },
                "UpdateCartItemRequest": {
                    "type": "object",
                    "required": ["quantity"],
                    "properties": {
                        "quantity": {"type": "integer"},
                    },
                },
                "CartResponse": {
                    "type": "object",
                    "properties": {
                        "cart_id": {"type": "string"},
                        "items": {"type": "array", "items": {"type": "object"}},
                        "total": {"type": "number"},
                    },
                },
                "CheckoutRequest": {
                    "type": "object",
                    "properties": {
                        "shipping_address_id": {"type": "string"},
                        "payment_method": {"type": "string"},
                    },
                },
                "CheckoutResponse": {
                    "type": "object",
                    "properties": {
                        "checkout_id": {"type": "string"},
                        "total_amount": {"type": "number"},
                        "status": {"type": "string"},
                    },
                },
                "CreateOrderRequest": {
                    "type": "object",
                    "properties": {
                        "checkout_id": {"type": "string"},
                    },
                },
                "OrderResponse": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "status": {"type": "string"},
                        "total_amount": {"type": "number"},
                    },
                },
                "OrderListResponse": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/OrderResponse"},
                        }
                    },
                },
            }
        },
    }


def save_openapi_yaml(openapi_doc: dict, output_file: str) -> None:
    """
    Saves OpenAPI document as YAML.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        yaml.safe_dump(openapi_doc, file, sort_keys=False, allow_unicode=True)
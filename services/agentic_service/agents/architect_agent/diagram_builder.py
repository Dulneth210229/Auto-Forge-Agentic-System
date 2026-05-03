from agents.architect_agent.schemas import DBPack, APIEndpoint


def build_use_case_diagram() -> str:
    """
    Generates a Mermaid flowchart-style use case diagram.

    Mermaid does not have native UML use-case syntax,
    so we use flowchart syntax to visually represent actors and use cases.
    """
    return """
flowchart LR
    Customer((Customer))
    Admin((Admin))
    PaymentGateway((Mock Payment Service))

    UC1[Register / Login]
    UC2[Browse Products]
    UC3[View Product Details]
    UC4[Search Products]
    UC5[Manage Cart]
    UC6[Checkout]
    UC7[Place Order]
    UC8[View Order History]
    UC9[Manage Products]

    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC4
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8

    Admin --> UC1
    Admin --> UC9

    UC6 --> PaymentGateway
""".strip()


def build_class_diagram(db_pack: DBPack) -> str:
    """
    Generates a valid Mermaid class diagram from DBPack.

    Important Mermaid syntax rule:
    Class fields should be written without putting braces on the same line
    as the class declaration in some Mermaid CLI versions.

    Safer format:
        class User
        User : uuid id
        User : string email

    This avoids parse errors like:
        class Category { uuid id }
    """

    lines = ["classDiagram"]

    # Create class attributes
    for entity in db_pack.entities:
        class_name = entity.name.replace(" ", "")

        lines.append(f"    class {class_name}")

        for attribute in entity.attributes:
            required_marker = "" if attribute.required else "?"
            attribute_type = attribute.type.replace(" ", "_")
            attribute_name = attribute.name.replace(" ", "_")

            lines.append(
                f"    {class_name} : {attribute_type} {attribute_name}{required_marker}"
            )

    lines.append("")

    # Create relationships
    relationship_map = {
        "1 to 1": '"1" --> "1"',
        "1 to many": '"1" --> "*"',
        "many to many": '"*" --> "*"',
    }

    for relationship in db_pack.relationships:
        source = relationship.source.replace(" ", "")
        target = relationship.target.replace(" ", "")
        mermaid_relation = relationship_map.get(relationship.relationship, "-->")

        # Keep relationship labels short to avoid Mermaid parsing issues.
        label = relationship.relationship.replace(" ", "_")

        lines.append(
            f"    {source} {mermaid_relation} {target} : {label}"
        )

    return "\n".join(lines)


def build_checkout_sequence_diagram() -> str:
    """
    Generates checkout sequence diagram.

    This shows the runtime interaction between user, frontend, APIs, payment,
    and database during checkout.
    """
    return """
sequenceDiagram
    actor Customer
    participant Frontend
    participant CartAPI as Cart API
    participant CheckoutAPI as Checkout API
    participant PaymentService as Mock Payment Service
    participant OrderAPI as Order API
    participant Database

    Customer->>Frontend: Click Checkout
    Frontend->>CartAPI: GET /cart
    CartAPI->>Database: Load cart and cart items
    Database-->>CartAPI: Cart data
    CartAPI-->>Frontend: Cart response

    Frontend->>CheckoutAPI: POST /checkout
    CheckoutAPI->>Database: Validate stock and pricing
    Database-->>CheckoutAPI: Validation result

    CheckoutAPI->>PaymentService: Process mock payment
    PaymentService-->>CheckoutAPI: Payment success

    CheckoutAPI->>OrderAPI: Create order request
    OrderAPI->>Database: Save order and order items
    Database-->>OrderAPI: Order saved
    OrderAPI-->>CheckoutAPI: Order response
    CheckoutAPI-->>Frontend: Checkout success
    Frontend-->>Customer: Show order confirmation
""".strip()


def build_order_history_sequence_diagram() -> str:
    """
    Generates order history sequence diagram.
    """
    return """
sequenceDiagram
    actor Customer
    participant Frontend
    participant OrderAPI as Order API
    participant Database

    Customer->>Frontend: Open Order History
    Frontend->>OrderAPI: GET /orders
    OrderAPI->>Database: Fetch orders by user ID
    Database-->>OrderAPI: Order list
    OrderAPI-->>Frontend: Order history response
    Frontend-->>Customer: Display previous orders
""".strip()


def build_architecture_flow_diagram(api_endpoints: list[APIEndpoint]) -> str:
    """
    Generates a visual architecture flow diagram.

    This is not a component list diagram.
    It shows high-level runtime interaction between frontend, modules, and DB.
    """
    tags = sorted(set(endpoint.tag for endpoint in api_endpoints))

    lines = [
        "flowchart TB",
        "    User((User))",
        "    Frontend[Frontend Web App]",
        "    Database[(Database)]",
        "",
        "    User --> Frontend",
    ]

    for tag in tags:
        safe_name = tag.replace(" ", "")
        lines.append(f"    Frontend --> {safe_name}[{tag} Module]")
        lines.append(f"    {safe_name} --> Database")

    return "\n".join(lines)
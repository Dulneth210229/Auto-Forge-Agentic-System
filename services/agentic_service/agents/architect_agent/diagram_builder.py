from agents.architect_agent.schemas import DBPack, APIEndpoint


def build_usecase_puml() -> str:
    """
    Generates a PlantUML use case diagram.

    This is saved as .puml and later converted into .png using PlantUML.
    """
    return """
@startuml
left to right direction

actor Customer
actor Admin
actor "Mock Payment Service" as PaymentService

rectangle "E-commerce System" {
    usecase "Register / Login" as UC1
    usecase "Browse Products" as UC2
    usecase "View Product Details" as UC3
    usecase "Search Products" as UC4
    usecase "Manage Cart" as UC5
    usecase "Checkout" as UC6
    usecase "Place Order" as UC7
    usecase "View Order History" as UC8
    usecase "Manage Products" as UC9
}

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

UC6 --> PaymentService
@enduml
""".strip()


def build_class_puml(db_pack: DBPack) -> str:
    """
    Generates a PlantUML class diagram from DBPack.
    """
    lines = ["@startuml", "skinparam classAttributeIconSize 0", ""]

    for entity in db_pack.entities:
        class_name = entity.name.replace(" ", "")
        lines.append(f"class {class_name} {{")

        for attribute in entity.attributes:
            optional_marker = "" if attribute.required else " {optional}"
            lines.append(f"  {attribute.type} {attribute.name}{optional_marker}")

        lines.append("}")
        lines.append("")

    relation_map = {
        "1 to 1": '"1" -- "1"',
        "1 to many": '"1" -- "*"',
        "many to many": '"*" -- "*"',
    }

    for relationship in db_pack.relationships:
        source = relationship.source.replace(" ", "")
        target = relationship.target.replace(" ", "")
        relation = relation_map.get(relationship.relationship, "--")
        lines.append(f"{source} {relation} {target} : {relationship.relationship}")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def build_sequence_checkout_puml() -> str:
    """
    Generates checkout sequence diagram in PlantUML.
    """
    return """
@startuml
actor Customer
participant Frontend
participant "Cart API" as CartAPI
participant "Checkout API" as CheckoutAPI
participant "Mock Payment Service" as PaymentService
participant "Order API" as OrderAPI
database Database

Customer -> Frontend : Click Checkout
Frontend -> CartAPI : GET /cart
CartAPI -> Database : Load cart and cart items
Database --> CartAPI : Cart data
CartAPI --> Frontend : Cart response

Frontend -> CheckoutAPI : POST /checkout
CheckoutAPI -> Database : Validate stock and pricing
Database --> CheckoutAPI : Validation result

CheckoutAPI -> PaymentService : Process mock payment
PaymentService --> CheckoutAPI : Payment success

CheckoutAPI -> OrderAPI : Create order request
OrderAPI -> Database : Save order and order items
Database --> OrderAPI : Order saved
OrderAPI --> CheckoutAPI : Order response
CheckoutAPI --> Frontend : Checkout success
Frontend --> Customer : Show order confirmation
@enduml
""".strip()


def build_sequence_order_history_puml() -> str:
    """
    Generates order history sequence diagram in PlantUML.
    """
    return """
@startuml
actor Customer
participant Frontend
participant "Order API" as OrderAPI
database Database

Customer -> Frontend : Open Order History
Frontend -> OrderAPI : GET /orders
OrderAPI -> Database : Fetch orders by user ID
Database --> OrderAPI : Order list
OrderAPI --> Frontend : Order history response
Frontend --> Customer : Display previous orders
@enduml
""".strip()


def build_architecture_flow_puml(api_endpoints: list[APIEndpoint]) -> str:
    """
    Generates a high-level architecture flow diagram in PlantUML.

    This is NOT a component list diagram.
    It is a simple high-level interaction view.
    """
    tags = sorted(set(endpoint.tag for endpoint in api_endpoints))

    lines = [
        "@startuml",
        "actor User",
        "rectangle \"Frontend Web App\" as Frontend",
        "database \"Database\" as DB",
        "",
        "User --> Frontend",
    ]

    for tag in tags:
        alias = tag.replace(" ", "")
        lines.append(f'rectangle "{tag} Module" as {alias}')
        lines.append(f"Frontend --> {alias}")
        lines.append(f"{alias} --> DB")

    lines.append("@enduml")

    return "\n".join(lines)
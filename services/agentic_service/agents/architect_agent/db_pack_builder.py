from agents.architect_agent.schemas import DBPack, DBEntity, DBAttribute, DBRelationship


def build_db_pack(project_name: str, version: str) -> DBPack:
    """
    Builds a stable first-version DB design for an E-commerce MVP.

    Why programmatic?
    - More reliable than asking an LLM to invent DB structure every time.
    - Easier to validate.
    - Easier to convert into class diagrams and later code models.
    """

    entities = [
        DBEntity(
            id="DE-001",
            name="User",
            description="Represents a customer or admin user.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique user ID."),
                DBAttribute(name="name", type="string", description="Full name of the user."),
                DBAttribute(name="email", type="string", description="Unique email address."),
                DBAttribute(name="password_hash", type="string", description="Hashed password."),
                DBAttribute(name="role", type="string", description="User role such as CUSTOMER or ADMIN."),
                DBAttribute(name="created_at", type="datetime", description="Account creation timestamp."),
            ],
        ),
        DBEntity(
            id="DE-002",
            name="Category",
            description="Represents a product category.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique category ID."),
                DBAttribute(name="name", type="string", description="Category name."),
                DBAttribute(name="description", type="string", required=False, description="Category description."),
            ],
        ),
        DBEntity(
            id="DE-003",
            name="Product",
            description="Represents a product available for sale.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique product ID."),
                DBAttribute(name="category_id", type="uuid", description="Related category ID."),
                DBAttribute(name="name", type="string", description="Product name."),
                DBAttribute(name="description", type="text", description="Product description."),
                DBAttribute(name="price", type="decimal", description="Product selling price."),
                DBAttribute(name="stock_quantity", type="integer", description="Available stock quantity."),
                DBAttribute(name="image_url", type="string", required=False, description="Product image URL."),
                DBAttribute(name="is_active", type="boolean", description="Whether product is active."),
            ],
        ),
        DBEntity(
            id="DE-004",
            name="Cart",
            description="Represents a customer's shopping cart.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique cart ID."),
                DBAttribute(name="user_id", type="uuid", description="Owner user ID."),
                DBAttribute(name="created_at", type="datetime", description="Cart creation timestamp."),
                DBAttribute(name="updated_at", type="datetime", description="Cart update timestamp."),
            ],
        ),
        DBEntity(
            id="DE-005",
            name="CartItem",
            description="Represents one product item inside a cart.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique cart item ID."),
                DBAttribute(name="cart_id", type="uuid", description="Related cart ID."),
                DBAttribute(name="product_id", type="uuid", description="Related product ID."),
                DBAttribute(name="quantity", type="integer", description="Product quantity in cart."),
                DBAttribute(name="unit_price", type="decimal", description="Price at the time of adding to cart."),
            ],
        ),
        DBEntity(
            id="DE-006",
            name="Order",
            description="Represents a placed customer order.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique order ID."),
                DBAttribute(name="user_id", type="uuid", description="Customer who placed the order."),
                DBAttribute(name="status", type="string", description="Order status."),
                DBAttribute(name="total_amount", type="decimal", description="Final order total."),
                DBAttribute(name="created_at", type="datetime", description="Order creation timestamp."),
            ],
        ),
        DBEntity(
            id="DE-007",
            name="OrderItem",
            description="Represents one product line item inside an order.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique order item ID."),
                DBAttribute(name="order_id", type="uuid", description="Related order ID."),
                DBAttribute(name="product_id", type="uuid", description="Related product ID."),
                DBAttribute(name="quantity", type="integer", description="Purchased quantity."),
                DBAttribute(name="unit_price", type="decimal", description="Product price at purchase time."),
            ],
        ),
        DBEntity(
            id="DE-008",
            name="Payment",
            description="Represents payment information for an order.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique payment ID."),
                DBAttribute(name="order_id", type="uuid", description="Related order ID."),
                DBAttribute(name="method", type="string", description="Payment method."),
                DBAttribute(name="status", type="string", description="Payment status."),
                DBAttribute(name="transaction_reference", type="string", required=False, description="Mock or real payment reference."),
            ],
        ),
        DBEntity(
            id="DE-009",
            name="Address",
            description="Represents customer shipping or billing address.",
            attributes=[
                DBAttribute(name="id", type="uuid", description="Unique address ID."),
                DBAttribute(name="user_id", type="uuid", description="Owner user ID."),
                DBAttribute(name="line1", type="string", description="Address line 1."),
                DBAttribute(name="city", type="string", description="City."),
                DBAttribute(name="postal_code", type="string", description="Postal code."),
                DBAttribute(name="country", type="string", description="Country."),
            ],
        ),
    ]

    relationships = [
        DBRelationship(source="User", target="Cart", relationship="1 to 1", description="One user owns one active cart."),
        DBRelationship(source="Cart", target="CartItem", relationship="1 to many", description="One cart contains many cart items."),
        DBRelationship(source="Product", target="CartItem", relationship="1 to many", description="A product can appear in many cart items."),
        DBRelationship(source="User", target="Order", relationship="1 to many", description="One user can place many orders."),
        DBRelationship(source="Order", target="OrderItem", relationship="1 to many", description="One order contains many order items."),
        DBRelationship(source="Product", target="OrderItem", relationship="1 to many", description="A product can appear in many order items."),
        DBRelationship(source="Order", target="Payment", relationship="1 to 1", description="One order has one payment record."),
        DBRelationship(source="Category", target="Product", relationship="1 to many", description="One category contains many products."),
        DBRelationship(source="User", target="Address", relationship="1 to many", description="One user can have many addresses."),
    ]

    return DBPack(
        project_name=project_name,
        version=version,
        database_type="relational",
        entities=entities,
        relationships=relationships,
        indexes=[
            "User.email unique index",
            "Product.category_id index",
            "Product.name search index",
            "Cart.user_id index",
            "Order.user_id index",
            "Order.status index",
        ],
        constraints=[
            "Product.stock_quantity must be greater than or equal to 0.",
            "Product.price must be greater than or equal to 0.",
            "CartItem.quantity must be greater than 0.",
            "Order.total_amount must be greater than or equal to 0.",
            "User.email must be unique.",
        ],
    )
# Database Design Pack: AutoForge Shop

**Version:** v5  
**Database Type:** relational

---

## 1. Entities

### DE-001 — User

Represents a customer or admin user.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique user ID. |
| name | string | True | Full name of the user. |
| email | string | True | Unique email address. |
| password_hash | string | True | Hashed password. |
| role | string | True | User role such as CUSTOMER or ADMIN. |
| created_at | datetime | True | Account creation timestamp. |

### DE-002 — Category

Represents a product category.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique category ID. |
| name | string | True | Category name. |
| description | string | False | Category description. |

### DE-003 — Product

Represents a product available for sale.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique product ID. |
| category_id | uuid | True | Related category ID. |
| name | string | True | Product name. |
| description | text | True | Product description. |
| price | decimal | True | Product selling price. |
| stock_quantity | integer | True | Available stock quantity. |
| image_url | string | False | Product image URL. |
| is_active | boolean | True | Whether product is active. |

### DE-004 — Cart

Represents a customer's shopping cart.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique cart ID. |
| user_id | uuid | True | Owner user ID. |
| created_at | datetime | True | Cart creation timestamp. |
| updated_at | datetime | True | Cart update timestamp. |

### DE-005 — CartItem

Represents one product item inside a cart.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique cart item ID. |
| cart_id | uuid | True | Related cart ID. |
| product_id | uuid | True | Related product ID. |
| quantity | integer | True | Product quantity in cart. |
| unit_price | decimal | True | Price at the time of adding to cart. |

### DE-006 — Order

Represents a placed customer order.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique order ID. |
| user_id | uuid | True | Customer who placed the order. |
| status | string | True | Order status. |
| total_amount | decimal | True | Final order total. |
| created_at | datetime | True | Order creation timestamp. |

### DE-007 — OrderItem

Represents one product line item inside an order.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique order item ID. |
| order_id | uuid | True | Related order ID. |
| product_id | uuid | True | Related product ID. |
| quantity | integer | True | Purchased quantity. |
| unit_price | decimal | True | Product price at purchase time. |

### DE-008 — Payment

Represents payment information for an order.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique payment ID. |
| order_id | uuid | True | Related order ID. |
| method | string | True | Payment method. |
| status | string | True | Payment status. |
| transaction_reference | string | False | Mock or real payment reference. |

### DE-009 — Address

Represents customer shipping or billing address.

| Attribute | Type | Required | Description |
|---|---|---:|---|
| id | uuid | True | Unique address ID. |
| user_id | uuid | True | Owner user ID. |
| line1 | string | True | Address line 1. |
| city | string | True | City. |
| postal_code | string | True | Postal code. |
| country | string | True | Country. |


---

## 2. Relationships

- **User → Cart**: 1 to 1 — One user owns one active cart.
- **Cart → CartItem**: 1 to many — One cart contains many cart items.
- **Product → CartItem**: 1 to many — A product can appear in many cart items.
- **User → Order**: 1 to many — One user can place many orders.
- **Order → OrderItem**: 1 to many — One order contains many order items.
- **Product → OrderItem**: 1 to many — A product can appear in many order items.
- **Order → Payment**: 1 to 1 — One order has one payment record.
- **Category → Product**: 1 to many — One category contains many products.
- **User → Address**: 1 to many — One user can have many addresses.

---

## 3. Indexes

- User.email unique index
- Product.category_id index
- Product.name search index
- Cart.user_id index
- Order.user_id index
- Order.status index

---

## 4. Constraints

- Product.stock_quantity must be greater than or equal to 0.
- Product.price must be greater than or equal to 0.
- CartItem.quantity must be greater than 0.
- Order.total_amount must be greater than or equal to 0.
- User.email must be unique.

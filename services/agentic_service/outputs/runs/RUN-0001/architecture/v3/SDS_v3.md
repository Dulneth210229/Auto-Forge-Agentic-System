# Software Design Specification: AutoForge Shop

**Version:** v3  
**Architecture Style:** modular_monolith

---

## 1. Architecture Overview

The system follows a modular monolith architecture for the MVP. The application is deployed as one backend service, but internally separated into Identity, Catalog, Cart, Checkout, Order, and Admin modules.

---

## 2. Technology Stack

- Python FastAPI backend
- Relational database such as PostgreSQL or SQLite
- OpenAPI 3.0 for API contract
- PlantUML + Graphviz for diagrams
- Pydantic for validation

---

## 3. Logical Modules

### MOD-001 — Identity Module

Handles user registration, login, authentication, and role-based access.

**Related Requirements:** FR-001

### MOD-002 — Catalog Module

Handles product browsing, searching, filtering, and product details.

**Related Requirements:** FR-001, FR-002, FR-003

### MOD-003 — Cart Module

Handles cart creation, adding items, updating quantities, and removing items.

**Related Requirements:** FR-003

### MOD-004 — Checkout Module

Validates cart, calculates totals, applies business rules, and prepares order creation.

**Related Requirements:** FR-004, FR-005

### MOD-005 — Order Module

Handles order placement, order status, and order history.

**Related Requirements:** FR-004, FR-005, FR-006

### MOD-006 — Admin Module

Handles basic product management for administrators.

**Related Requirements:** FR-001


---

## 4. API Endpoint Summary

### API-001 — POST /auth/register

**Tag:** Identity

Creates a new customer account.

**Request Schema:** RegisterRequest  
**Response Schema:** AuthResponse  
**Related Requirements:** FR-001

### API-002 — POST /auth/login

**Tag:** Identity

Authenticates a user and returns an access token.

**Request Schema:** LoginRequest  
**Response Schema:** AuthResponse  
**Related Requirements:** FR-001

### API-003 — GET /products

**Tag:** Catalog

Returns available products for catalog browsing.

**Request Schema:** None  
**Response Schema:** ProductListResponse  
**Related Requirements:** FR-001, FR-002, FR-003

### API-004 — GET /products/{product_id}

**Tag:** Catalog

Returns detailed information for a selected product.

**Request Schema:** None  
**Response Schema:** ProductResponse  
**Related Requirements:** FR-001, FR-002, FR-003

### API-005 — GET /cart

**Tag:** Cart

Returns the current user's cart.

**Request Schema:** None  
**Response Schema:** CartResponse  
**Related Requirements:** FR-003

### API-006 — POST /cart/items

**Tag:** Cart

Adds a selected product to the cart.

**Request Schema:** AddCartItemRequest  
**Response Schema:** CartResponse  
**Related Requirements:** FR-003

### API-007 — PUT /cart/items/{item_id}

**Tag:** Cart

Updates item quantity in the cart.

**Request Schema:** UpdateCartItemRequest  
**Response Schema:** CartResponse  
**Related Requirements:** FR-003

### API-008 — DELETE /cart/items/{item_id}

**Tag:** Cart

Removes a product item from the cart.

**Request Schema:** None  
**Response Schema:** CartResponse  
**Related Requirements:** FR-003

### API-009 — POST /checkout

**Tag:** Checkout

Validates cart, calculates total, and prepares order placement.

**Request Schema:** CheckoutRequest  
**Response Schema:** CheckoutResponse  
**Related Requirements:** FR-004

### API-010 — POST /orders

**Tag:** Order

Creates an order from checkout data.

**Request Schema:** CreateOrderRequest  
**Response Schema:** OrderResponse  
**Related Requirements:** FR-004, FR-005, FR-006

### API-011 — GET /orders

**Tag:** Order

Returns order history for the authenticated customer.

**Request Schema:** None  
**Response Schema:** OrderListResponse  
**Related Requirements:** FR-005, FR-006

### API-012 — POST /admin/products

**Tag:** Admin

Allows admin to create a product.

**Request Schema:** ProductCreateRequest  
**Response Schema:** ProductResponse  
**Related Requirements:** FR-001

### API-013 — GET /products/search

**Tag:** Catalog

Searches products using keyword, category, and price range filters.

**Request Schema:** None  
**Response Schema:** ProductListResponse  
**Related Requirements:** FR-SEARCH


---

## 5. Security Considerations

- Use token-based authentication for protected endpoints.
- Hash user passwords before storage.
- Validate product stock before checkout.
- Prevent users from accessing other users' carts and orders.
- Use server-side validation for all request payloads.

---

## 6. Deployment Assumptions

- The MVP can run locally using FastAPI and a relational database.
- Docker support can be added later.
- Payment is mocked unless real payment integration is required.

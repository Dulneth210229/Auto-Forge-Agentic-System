# Software Requirements Specification: AutoForge E-commerce Demo

**Version:** v4  
**Domain:** E-commerce

---

## 1. Purpose

To build a functional web platform enabling customers to browse, purchase, and track products, and allowing administrators to manage inventory and orders.

---

## 2. Scope

### In Scope

- Product browsing and search
- Detailed product viewing
- Shopping cart management
- Multi-step checkout process
- Order placement and confirmation
- Customer order history viewing
- Basic Admin product and order management
- User registration and profile management

### Out of Scope

- Advanced marketing integrations (e.g., loyalty points)
- Multi-currency support
- Complex tax calculation rules

---

## 3. Roles

- End-user who browses, adds items to cart, and places orders.
- Internal user responsible for managing products, inventory, and viewing/updating orders.

---

## 4. Stakeholders


---

## 5. Workflows

- {"workflow_name": "Customer Purchase Flow", "steps": ["Browse Catalog -> View Product Details -> Add to Cart -> Review Cart -> Checkout -> Place Order -> Receive Confirmation"]}
- {"workflow_name": "Admin Inventory Update Flow", "steps": ["Login -> Navigate to Product Management -> Edit Product Details -> Update Stock/Price -> Save"]}

---

## 6. Business Rules

- {"rule_id": "BR-001", "rule": "A customer must be logged in or provide shipping details to proceed to checkout."}
- {"rule_id": "BR-002", "rule": "Product stock cannot be negative; the system must prevent overselling."}
- {"rule_id": "BR-003", "rule": "The total order price must equal the sum of (Quantity * Unit Price) plus applicable shipping costs."}

---

## 7. Constraints

- Use local generated outputs folder
- Use FastAPI backend
- Use simple frontend for demonstration

---

## 8. Assumptions

- Payment gateway is mocked (no live transaction processing required)
- Inventory data can be sample data
- Admin authentication can be basic for MVP

---

## 9. Functional Requirements

### FR-001 — Product Catalog Browsing

**Priority:** Must

The system must allow customers to view a list of available products with basic filtering and search functionality.

**Acceptance Criteria:**

- **AC-001:** The system must display product name, price, and image thumbnail on the catalog page.
- **AC-002:** The system must allow filtering by category.

### FR-002 — Product Detail Viewing

**Priority:** Must

The system must display comprehensive details for a selected product.

**Acceptance Criteria:**

- **AC-003:** The product detail page must display description, price, available stock, and multiple images.
- **AC-004:** The user must be able to select a quantity and add the item to the cart.

### FR-003 — Shopping Cart Management

**Priority:** Must

The system must allow users to add, modify quantities, and remove items from a persistent shopping cart.

**Acceptance Criteria:**

- **AC-005:** The cart must display the subtotal, tax, and total price.
- **AC-006:** The user must be able to update the quantity of an item in the cart.

### FR-004 — Checkout Process

**Priority:** Must

The system must guide the user through a multi-step checkout process (Shipping -> Billing -> Payment).

**Acceptance Criteria:**

- **AC-007:** The system must validate required fields for shipping and billing addresses.
- **AC-008:** The system must calculate and display shipping costs based on the provided address.

### FR-005 — Order Placement

**Priority:** Must

The system must finalize the transaction, process payment (mocked), and create a permanent order record.

**Acceptance Criteria:**

- **AC-009:** Upon successful placement, the system must generate a unique Order ID and confirmation page.
- **AC-010:** The system must decrement the stock count for all purchased items.

### FR-006 — Order History Viewing

**Priority:** Should

The system must allow logged-in customers to view a list of their past orders and their current status.

**Acceptance Criteria:**

- **AC-011:** The order history page must display the order date, total amount, and current status (e.g., Shipped, Delivered).

### FR-007 — Admin Product Management

**Priority:** Must

Admin users must be able to create, read, update, and delete product listings.

**Acceptance Criteria:**

- **AC-012:** Admin must be able to update product price and stock level.
- **AC-013:** Admin must be able to assign product categories.

### FR-008 — Admin Order Fulfillment

**Priority:** Must

Admin users must be able to view all placed orders and update their fulfillment status.

**Acceptance Criteria:**

- **AC-014:** Admin must be able to change the order status (e.g., Pending -> Shipped).
- **AC-015:** The system must log the user who changed the order status and the timestamp.

### FR-009 — User Account Management

**Priority:** Must

The system must allow customers to register, log in, and manage their personal profile and shipping addresses.

**Acceptance Criteria:**

- **AC-016:** The user must be able to register an account using a unique email and password.
- **AC-017:** The user must be able to view, edit, and save multiple shipping addresses.

### FR-010 — Advanced Search and Filtering

**Priority:** Should

The system must enhance product browsing by allowing users to filter results by attributes (e.g., brand, price range) and sort by criteria (e.g., rating, price).

**Acceptance Criteria:**

- **AC-018:** The system must allow filtering of products by brand name.
- **AC-019:** The system must allow sorting of the product list by price (ascending/descending).


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The platform must load critical pages (Catalog, Product Detail) within 3 seconds under normal load.

**Acceptance Criteria:**

- **AC-020:** The catalog page must load fully within 3 seconds when displaying up to 100 products.

### NFR-002 — Security

All user authentication and sensitive data (passwords, addresses) must be handled securely.

**Acceptance Criteria:**

- **AC-021:** Passwords must be hashed using industry-standard algorithms (e.g., bcrypt).
- **AC-022:** Admin endpoints must require role-based access control (RBAC).

### NFR-003 — Usability

The platform must be fully responsive and usable across major devices (desktop, tablet, mobile).

**Acceptance Criteria:**

- **AC-023:** The layout must maintain functionality and readability when viewed on a standard mobile viewport (320px width).


---

## 11. Use Cases

### UC-001 — Place Order as Customer

**Actor:** Customer

**Preconditions:**

- Customer is logged in.
- Cart contains at least one item.

**Main Flow:**

1. Customer navigates to checkout.
2. Customer enters/confirms shipping details.
3. Customer selects payment method (mocked).
4. Customer submits order.
5. System validates stock and calculates final total.
6. System processes payment and creates order record.

**Alternative Flows:**

- If stock is insufficient, the system notifies the user and prompts for quantity reduction.
- If payment fails, the system displays an error and allows retry.

**Related Requirements:** FR-003, FR-004, FR-005, FR-008

### UC-002 — Browse and View Product Details

**Actor:** Customer

**Preconditions:**

- Customer is on the e-commerce site.

**Main Flow:**

1. Customer searches or browses the catalog.
2. Customer clicks on a product listing.
3. System displays the detailed product page.
4. Customer adds the item to the cart.

**Alternative Flows:**


**Related Requirements:** FR-001, FR-002, FR-003

### UC-003 — Manage Inventory (Admin)

**Actor:** Admin User

**Preconditions:**

- Admin user is logged in with appropriate permissions.

**Main Flow:**

1. Admin navigates to the product management dashboard.
2. Admin selects a product to edit.
3. Admin updates stock count, price, or description.
4. Admin saves changes.

**Alternative Flows:**


**Related Requirements:** FR-007


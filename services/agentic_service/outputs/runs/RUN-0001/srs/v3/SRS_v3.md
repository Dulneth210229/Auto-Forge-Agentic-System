# Software Requirements Specification: AutoForge E-commerce Demo

**Version:** v3  
**Domain:** E-commerce

---

## 1. Purpose

To build a functional web platform enabling customers to browse products, manage shopping carts, complete secure checkouts, and view their order history, while providing administrative tools for product management.

---

## 2. Scope

### In Scope

- Product browsing and search
- Detailed product viewing
- Shopping cart management (add, remove, update quantity)
- Multi-step checkout process
- Order placement and confirmation
- Customer order history viewing
- Basic Admin product management

### Out of Scope

- Advanced recommendation engines
- Multi-currency support
- Loyalty points system
- Live chat support integration

---

## 3. Roles

- End-user who browses, selects, and purchases products.
- Internal user responsible for managing products, inventory, and viewing orders.

---

## 4. Stakeholders


---

## 5. Workflows

- {"workflow_name": "Customer Purchase Flow", "steps": ["Browse Catalog -> View Product Details -> Add to Cart -> Review Cart -> Checkout -> Place Order -> Receive Confirmation"]}
- {"workflow_name": "Admin Product Update Flow", "steps": ["Login -> Navigate to Product Management -> Select Product -> Update Details/Inventory -> Save"]}

---

## 6. Business Rules

- {"rule_id": "BR-001", "rule": "Product availability must be checked against current inventory levels before checkout."}
- {"rule_id": "BR-002", "rule": "A customer must be logged in or provide shipping details to complete the checkout process."}
- {"rule_id": "BR-003", "rule": "Order total must equal (Sum of (Product Price * Quantity)) + Shipping Cost."}

---

## 7. Constraints

- Use local generated outputs folder
- Use FastAPI backend
- Use simple frontend for demonstration

---

## 8. Assumptions

- Payment gateway is mocked
- Inventory data can be sample data
- Admin authentication can be basic for MVP

---

## 9. Functional Requirements

### FR-001 — Product Catalog Browsing

**Priority:** Must

The system must allow customers to browse products by category and search using keywords.

**Acceptance Criteria:**

- **AC-001:** The system must display a list of products with name, price, and image thumbnail on the catalog page.
- **AC-002:** The system must filter products based on selected categories.

### FR-002 — Product Detail Viewing

**Priority:** Must

The system must display comprehensive information for a single product.

**Acceptance Criteria:**

- **AC-003:** The product detail page must display the full description, price, available stock, and images.
- **AC-004:** The user must be able to select a quantity and add the item to the cart.

### FR-003 — Shopping Cart Management

**Priority:** Must

The system must allow users to add, view, modify, and remove items from a persistent shopping cart.

**Acceptance Criteria:**

- **AC-005:** The cart must display the subtotal, tax, and estimated shipping cost.
- **AC-006:** Users must be able to update the quantity of any item in the cart.

### FR-004 — Checkout Process

**Priority:** Must

The system must guide the user through a multi-step checkout process (Shipping -> Billing -> Payment).

**Acceptance Criteria:**

- **AC-007:** The system must validate required fields for shipping and billing addresses.
- **AC-008:** The system must calculate the final total including all applicable taxes and shipping fees.

### FR-005 — Order Placement

**Priority:** Must

The system must process the order, validate inventory, and generate a confirmation.

**Acceptance Criteria:**

- **AC-009:** Upon successful submission, the system must generate a unique order ID and confirm the order status as 'Processing'.
- **AC-010:** The system must decrement the inventory count for all purchased items.

### FR-006 — Order History Viewing

**Priority:** Should

The system must allow logged-in customers to view a list of their past orders and their details.

**Acceptance Criteria:**

- **AC-011:** The order history page must display the order date, total amount, and current status for all past orders.
- **AC-012:** The user must be able to view the detailed items and shipping information for a specific past order.

### FR-007 — Admin Product Management

**Priority:** Must

The Admin user must be able to create, read, update, and delete product listings and manage inventory.

**Acceptance Criteria:**

- **AC-013:** Admin must be able to update the price and description of an existing product.
- **AC-014:** Admin must be able to adjust the stock quantity for any product.


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The platform must load key pages (Catalog, Product Detail) within 3 seconds under normal load.

**Acceptance Criteria:**

- **AC-020:** Page load time for the main catalog page must be less than 3 seconds when tested with 100 concurrent users.

### NFR-002 — Security

All user authentication and payment data handling must be secured using industry best practices (e.g., HTTPS, hashing).

**Acceptance Criteria:**

- **AC-021:** User passwords must be stored using a strong hashing algorithm (e.g., bcrypt).
- **AC-022:** The checkout process must simulate secure data transmission, even if the payment gateway is mocked.

### NFR-003 — Usability

The platform must be fully responsive and usable across major devices (desktop, tablet, mobile).

**Acceptance Criteria:**

- **AC-023:** The layout must adapt correctly and remain functional when viewed on a standard mobile viewport (e.g., 375px width).


---

## 11. Use Cases

### UC-001 — Customer Purchases Product

**Actor:** Customer

**Preconditions:**

- Customer is logged in (optional)
- Product inventory is available

**Main Flow:**

1. Customer searches/browses catalog.
2. Customer views product details and adds item to cart.
3. Customer proceeds to checkout.
4. Customer enters shipping/billing details.
5. Customer confirms order and submits payment details.

**Alternative Flows:**

- If inventory is low, the system displays a warning and allows partial purchase.
- If payment fails, the system displays an error and allows retry.

**Related Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005

### UC-002 — Admin Manages Product Inventory

**Actor:** Admin User

**Preconditions:**

- Admin user is authenticated.

**Main Flow:**

1. Admin logs into the dashboard.
2. Admin navigates to the Product Management section.
3. Admin selects a product and updates its stock quantity or price.
4. Admin saves the changes.

**Alternative Flows:**

- If the product ID is invalid, the system displays an error message.

**Related Requirements:** FR-007

### UC-003 — Customer Views Order History

**Actor:** Customer

**Preconditions:**

- Customer is logged in.

**Main Flow:**

1. Customer navigates to 'My Orders'.
2. System retrieves and displays a list of all past orders.
3. Customer clicks on a specific order to view details.

**Alternative Flows:**


**Related Requirements:** FR-006


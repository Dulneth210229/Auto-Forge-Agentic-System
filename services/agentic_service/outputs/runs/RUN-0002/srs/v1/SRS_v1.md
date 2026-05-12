# Software Requirements Specification: AutoForge Shop

**Version:** v1  
**Domain:** E-commerce

---

## 1. Purpose

To provide a functional, web-based platform enabling customers to browse products, manage shopping carts, complete mock checkout processes, place orders, and view their order history.

---

## 2. Scope

### In Scope

- Product browsing and catalog viewing
- Viewing detailed product information
- Adding, updating, and removing items from a shopping cart
- Multi-step checkout process (shipping/payment mock)
- Order placement and confirmation
- Viewing historical order details

### Out of Scope

- Real payment gateway integration (PCI compliance)
- Mobile application development
- Advanced inventory management (e.g., low stock alerts)
- Customer account registration/login (MVP focuses on guest checkout)

---

## 3. Roles

- Customer
- Admin

---

## 4. Stakeholders

- **Business Analyst:** Defines and validates requirements.
- **Store Owner:** Manages products and order processing.

---

## 5. Workflows

- Customer Shopping Journey
- Order Fulfillment Workflow

---

## 6. Business Rules

- Only in-stock products can be ordered.
- Cart total must be calculated dynamically based on item prices and quantities.
- Payment processing is mocked for the MVP and does not interact with external financial systems.

---

## 7. Constraints

- The system must run locally (single instance deployment).
- The first version focuses strictly on catalog, cart, checkout, and orders.

---

## 8. Assumptions

- Users access the system through a standard modern web browser.
- Admin product management capabilities are deferred to a later phase.

---

## 9. Functional Requirements

### FR-001 — Product Catalog Browsing

**Priority:** Must

The system must allow customers to view a list of available products, supporting filtering and basic search.

**Acceptance Criteria:**

- **AC-001:** The system must display all active products on the main catalog page.
- **AC-002:** The system must allow filtering by category.
- **AC-003:** The system must display the product name, price, and availability status on the catalog listing.

### FR-002 — Product Detail Viewing

**Priority:** Must

The system must display comprehensive information for a selected product.

**Acceptance Criteria:**

- **AC-004:** The product detail page must display the full description, price, and SKU.
- **AC-005:** The user must be able to select a quantity and add the item to the cart from the detail page.
- **AC-006:** If a product is out of stock, the system must display a clear 'Out of Stock' message and disable the 'Add to Cart' button.

### FR-003 — Shopping Cart Management

**Priority:** Must

The system must allow users to manage items added to their cart.

**Acceptance Criteria:**

- **AC-007:** The cart must display the item name, quantity, unit price, and subtotal for every item.
- **AC-008:** Users must be able to increase or decrease the quantity of an item in the cart.
- **AC-009:** Users must be able to remove items entirely from the cart.
- **AC-010:** The cart must display a running total (subtotal) before taxes/shipping.

### FR-004 — Checkout Process

**Priority:** Must

The system must guide the user through the checkout steps.

**Acceptance Criteria:**

- **AC-011:** The checkout process must collect necessary shipping information (Name, Address, etc.).
- **AC-012:** The system must calculate and display the final total, including any mock taxes or shipping fees.
- **AC-013:** The system must provide a mock payment interface (e.g., accepting a dummy card number) to proceed.

### FR-005 — Order Placement

**Priority:** Must

The system must finalize the transaction and create a permanent order record.

**Acceptance Criteria:**

- **AC-014:** Upon successful mock payment, the system must generate a unique Order ID.
- **AC-015:** The system must confirm the order placement to the user and clear the shopping cart.

### FR-006 — Order History Viewing

**Priority:** Should

The system must allow the customer to view a list of their past orders.

**Acceptance Criteria:**

- **AC-016:** The order history page must list the Order ID, date, and total amount for each past order.
- **AC-017:** Clicking an order ID must display the detailed items, quantities, and final price breakdown for that specific order.


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The system must load all primary pages (Catalog, Product Detail, Cart) within 3 seconds under normal load.

**Acceptance Criteria:**

- **AC-018:** Page load time must be measured and maintained below 3 seconds.

### NFR-002 — Security

All user input fields (especially addresses and names) must be sanitized to prevent XSS and SQL injection attacks.

**Acceptance Criteria:**

- **AC-019:** The system must validate that all required fields are filled before submission.

### NFR-003 — Usability

The user interface must be intuitive, requiring minimal training for a first-time user to complete a purchase.

**Acceptance Criteria:**

- **AC-020:** The checkout flow must be linear and clearly guide the user from one step to the next.


---

## 11. Use Cases

### UC-001 — Customer Purchases Product

**Actor:** Customer

**Preconditions:**

- The product catalog must be populated with available items.

**Main Flow:**

1. Customer navigates to Catalog (FR-001).
2. Customer selects a product and views details (FR-002).
3. Customer adds item to cart (FR-003).
4. Customer proceeds to checkout (FR-004).
5. Customer provides shipping details and completes mock payment (FR-004, FR-005).
6. System confirms order and displays confirmation page (FR-005).

**Alternative Flows:**

- Customer removes item from cart before checkout.
- Customer fails mock payment and is prompted to retry.

**Related Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005

### UC-002 — Customer Views Order History

**Actor:** Customer

**Preconditions:**

- The customer must have placed at least one order.

**Main Flow:**

1. Customer navigates to Order History page (FR-006).
2. System displays list of past orders (FR-006).
3. Customer selects an order ID.
4. System displays detailed order breakdown (FR-006).

**Alternative Flows:**


**Related Requirements:** FR-006

### UC-003 — Admin Views Order Status

**Actor:** Admin

**Preconditions:**

- The Admin must be logged into the system.

**Main Flow:**

1. Admin accesses the Order Dashboard.
2. System displays a list of recent orders.
3. Admin views the order details and updates the status (e.g., 'Processing' to 'Shipped').

**Alternative Flows:**


**Related Requirements:** 


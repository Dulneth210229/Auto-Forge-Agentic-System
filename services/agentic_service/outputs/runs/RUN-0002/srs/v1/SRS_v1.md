# Software Requirements Specification: AutoForge Shop

**Version:** v1  
**Domain:** E-commerce

---

## 1. Purpose

To provide a functional, basic e-commerce platform allowing customers to browse products, manage a shopping cart, complete a mock checkout process, place orders, and view their order history.

---

## 2. Scope

### In Scope

- Product browsing and catalog viewing
- Detailed product information display
- Shopping cart management (add, remove, update quantity)
- Checkout process (shipping/billing info capture)
- Order placement and confirmation
- Customer order history viewing

### Out of Scope

- Real payment gateway integration
- Mobile application development
- Admin product management (CRUD)
- User authentication beyond basic session management

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

- Customer Shopping Flow
- Order Fulfillment Flow

---

## 6. Business Rules

- Only in-stock products can be ordered.
- Cart total must be calculated before checkout.
- Payment is mocked in the MVP.

---

## 7. Constraints

- The system must run locally.
- The first version focuses on catalog, cart, checkout, and orders.

---

## 8. Assumptions

- Users access the system through a web browser.
- Admin product management can be added after MVP.

---

## 9. Functional Requirements

### FR-001 — Product Catalog Browsing

**Priority:** Must

The system must allow customers to view a list of all available products with basic information (Name, Price, Image).

**Acceptance Criteria:**

- **AC-001:** The catalog page must display at least the product name, price, and a thumbnail image for every available item.
- **AC-002:** The system must allow filtering or sorting of products by category or price range.

### FR-002 — Product Details View

**Priority:** Must

The system must display comprehensive details for a selected product, including description, stock status, and variations (if applicable).

**Acceptance Criteria:**

- **AC-003:** The product detail page must display the full description, SKU, and current stock level.
- **AC-004:** The user must be able to select a quantity and add the item to the cart from the product detail page.

### FR-003 — Shopping Cart Management

**Priority:** Must

The system must allow customers to view, modify, and calculate the total cost of items in their shopping cart.

**Acceptance Criteria:**

- **AC-005:** The cart must display the product name, selected quantity, unit price, and subtotal for every item.
- **AC-006:** Users must be able to increase or decrease the quantity of an item in the cart.
- **AC-007:** Users must be able to remove items entirely from the cart.

### FR-004 — Checkout Process

**Priority:** Must

The system must guide the user through the checkout steps, collecting necessary shipping and billing information.

**Acceptance Criteria:**

- **AC-008:** The checkout process must require the user to input valid shipping address details.
- **AC-009:** The system must calculate and display the final total, including taxes and shipping fees (if applicable).

### FR-005 — Order Placement

**Priority:** Must

The system must finalize the transaction, process the order, and generate a confirmation.

**Acceptance Criteria:**

- **AC-010:** Upon successful submission, the system must generate a unique Order ID and confirm the order status as 'Processing'.
- **AC-011:** The system must record the order details, including items, quantities, final price, and shipping address.

### FR-006 — Order History Viewing

**Priority:** Must

The system must allow logged-in customers to view a list of their past orders and their current status.

**Acceptance Criteria:**

- **AC-012:** The order history page must list the Order ID, date placed, and current status (e.g., Processing, Shipped).
- **AC-013:** Clicking on an order ID must display a detailed summary of that specific order.


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The system must load critical pages (Catalog, Product Detail) within 3 seconds under normal load.

**Acceptance Criteria:**

- **AC-N001:** The catalog page must load fully within 3 seconds when accessed by 10 concurrent users.

### NFR-002 — Security

All user input (especially addresses and quantities) must be validated and sanitized to prevent injection attacks.

**Acceptance Criteria:**

- **AC-N002:** The system must reject non-numeric characters in quantity fields.

### NFR-003 — Usability

The user interface must be intuitive, requiring minimal training for a first-time user to complete a purchase.

**Acceptance Criteria:**

- **AC-N003:** The checkout process must be linear and clearly guide the user from shipping details to payment confirmation.


---

## 11. Use Cases

### UC-001 — Browse and Select Product

**Actor:** Customer

**Preconditions:**

- Customer is logged in (or browsing anonymously).

**Main Flow:**

1. Customer navigates to the catalog page.
2. Customer views product listings.
3. Customer selects a product of interest.
4. System displays the Product Details Page.

**Alternative Flows:**

- Customer uses search/filter functionality.
- Product is out of stock (System displays 'Out of Stock' message).

**Related Requirements:** FR-001, FR-002

### UC-002 — Manage Shopping Cart

**Actor:** Customer

**Preconditions:**

- Customer has added at least one item to the cart.

**Main Flow:**

1. Customer views the cart summary.
2. Customer adjusts quantity or removes an item.
3. System recalculates the cart total instantly.

**Alternative Flows:**

- Cart is empty (System prompts user to browse products).

**Related Requirements:** FR-003

### UC-003 — Complete Purchase

**Actor:** Customer

**Preconditions:**

- Cart contains items.
- Customer has valid shipping/billing information.

**Main Flow:**

1. Customer initiates checkout.
2. Customer enters/confirms shipping details.
3. Customer reviews the final order summary.
4. Customer submits the order (mock payment).
5. System confirms the order and redirects to the history page.

**Alternative Flows:**

- Validation error (e.g., invalid address) occurs (System prompts user to correct data).

**Related Requirements:** FR-004, FR-005

### UC-004 — View Order History

**Actor:** Customer

**Preconditions:**

- Customer is logged in.

**Main Flow:**

1. Customer navigates to 'My Orders'.
2. System displays a list of past orders.
3. Customer selects an order to view details.
4. System displays the full order summary and status.

**Alternative Flows:**


**Related Requirements:** FR-006


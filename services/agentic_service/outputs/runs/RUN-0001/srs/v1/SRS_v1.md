# Software Requirements Specification: AutoForge Shop

**Version:** v1  
**Domain:** E-commerce

---

## 1. Purpose

To build a simple E-commerce web platform that allows customers to browse products, manage a cart, checkout with mock payment, place orders, and view order history.

---

## 2. Scope

### In Scope


### Out of Scope

- Real payment gateway integration
- Mobile application
- Advanced recommendation engine

---

## 3. Roles

- A user who browses products, manages a cart, and places orders.
- A system administrator responsible for managing product sales and order processing.

---

## 4. Stakeholders

- **Business Analyst:** Collects and approves system requirements.
- **Store Owner:** Manages product sales and order processing.

---

## 5. Workflows


---

## 6. Business Rules

- Customers can only order products that are in stock.
- Checkout must calculate the total price before order placement.
- Payment is mocked in the MVP.

---

## 7. Constraints

- The system must run locally during development.
- The first version should focus on catalog, cart, checkout, and orders.

---

## 8. Assumptions

- Users access the system through a web browser.
- Admin product management can be added after the MVP.

---

## 9. Functional Requirements

### FR-001 — Product Browsing

**Priority:** Must

The system should allow customers to browse products by category, search for specific products, and view product details.

**Acceptance Criteria:**

- **AC-001:** The system displays a list of available products when browsing by category.

### FR-002 — Product Details

**Priority:** Must

The system should provide detailed information about each product, including price, description, and images.

**Acceptance Criteria:**

- **AC-002:** The system displays the product name, price, and brief description.

### FR-003 — Cart Operations

**Priority:** Must

The system should allow customers to add and remove products from their cart, update quantities, and view the cart summary.

**Acceptance Criteria:**

- **AC-003:** The system allows users to add a product to their cart.

### FR-004 — Checkout

**Priority:** Must

The system should provide a checkout process that calculates the total price, applies discounts (if available), and confirms the order.

**Acceptance Criteria:**

- **AC-004:** The system calculates the total price based on the products in the cart.

### FR-005 — Order Placement

**Priority:** Must

The system should allow customers to place orders, including processing payment and sending order confirmation emails.

**Acceptance Criteria:**

- **AC-005:** The system sends a confirmation email to the customer after successful order placement.

### FR-006 — Order History

**Priority:** Must

The system should provide customers with access to their order history, including order status and details.

**Acceptance Criteria:**

- **AC-006:** The system displays the customer's order history.


---

## 10. Non-Functional Requirements


---

## 11. Use Cases

### UC-001 — Customer Browsing

**Actor:** Customer

**Preconditions:**


**Main Flow:**

1. The customer browses products by category or searches for specific products.

**Alternative Flows:**


**Related Requirements:** FR-001, FR-002


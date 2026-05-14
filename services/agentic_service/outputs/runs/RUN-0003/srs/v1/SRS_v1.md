# Software Requirements Specification: AutoForge E-commerce Demo

**Version:** v1  
**Domain:** E-commerce

---

## 1. Purpose

To build an e-commerce web platform where customers can browse products, manage cart, checkout, and view orders.

---

## 2. Scope

### In Scope

- Product browsing and search
- Product details display
- Shopping cart management
- Checkout process
- Order placement
- Order history tracking
- User roles: Customers and Admin

### Out of Scope


---

## 3. Roles

- End user who browses products, adds to cart, checks out, and views order history - Customer
- User with access to manage products and view orders - Admin

---

## 4. Stakeholders


---

## 5. Workflows

- Customer navigates through product listings and filters based on criteria - Product Browsing
- Customer adds, removes, or updates quantities of items in the cart - Cart Management
- Customer proceeds to checkout, enters shipping and payment details, and confirms order - Checkout Process
- Customer views past orders and their status - Order History

---

## 6. Business Rules

- Inventory must be updated after order placement
- Cart items must be cleared after successful checkout
- Order status must be updated from 'pending' to 'confirmed' upon successful payment

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

### FR-001 — Browse Products

**Priority:** Must

Customers shall be able to browse products with filtering and sorting capabilities.

**Acceptance Criteria:**

- **AC-001:** User can filter products by category, price range, and brand

### FR-002 — View Product Details

**Priority:** Must

Customers shall be able to view detailed information of a product.

**Acceptance Criteria:**

- **AC-002:** Product details include name, description, price, images, and inventory status

### FR-003 — Manage Shopping Cart

**Priority:** Must

Customers shall be able to add, remove, and update quantities of items in the cart.

**Acceptance Criteria:**

- **AC-003:** Cart updates are reflected in real-time and persist during session

### FR-004 — Checkout Process

**Priority:** Must

Customers shall be able to proceed through checkout with shipping and payment information.

**Acceptance Criteria:**

- **AC-004:** Checkout process includes shipping address, payment method, and order review

### FR-005 — Place Order

**Priority:** Must

Customers shall be able to submit an order after completing checkout.

**Acceptance Criteria:**

- **AC-005:** Order confirmation is displayed with order number and expected delivery date

### FR-006 — View Order History

**Priority:** Must

Customers shall be able to view their past orders and their status.

**Acceptance Criteria:**

- **AC-006:** Order history displays order number, date, items, total amount, and status

### FR-007 — Admin Product Management

**Priority:** Should

Admin users shall be able to add, update, and delete products.

**Acceptance Criteria:**

- **AC-007:** Admin can upload product images, set price, and manage inventory levels


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The system shall load product listings within 2 seconds.

**Acceptance Criteria:**

- **AC-010:** Page load time for product listings is under 2 seconds on average

### NFR-002 — Security

User authentication and session management must be secure.

**Acceptance Criteria:**

- **AC-011:** User sessions are secured with token-based authentication

### NFR-003 — Usability

The interface shall be intuitive and responsive across devices.

**Acceptance Criteria:**

- **AC-012:** UI is responsive and usable on desktop, tablet, and mobile devices


---

## 11. Use Cases

### UC-001 — Browse Products

**Actor:** Customer

**Preconditions:**

- User is logged in or anonymous

**Main Flow:**

1. Customer navigates to product listing page
2. Customer applies filters or sorts items
3. System displays filtered/sorted product list

**Alternative Flows:**


**Related Requirements:** FR-001

### UC-002 — Add Product to Cart

**Actor:** Customer

**Preconditions:**

- Product is visible and in stock

**Main Flow:**

1. Customer selects a product
2. Customer clicks 'Add to Cart'
3. System updates cart with product

**Alternative Flows:**


**Related Requirements:** FR-003

### UC-003 — Complete Checkout

**Actor:** Customer

**Preconditions:**

- Cart contains at least one item

**Main Flow:**

1. Customer clicks 'Checkout'
2. Customer enters shipping and payment details
3. Customer confirms order
4. System processes order and displays confirmation

**Alternative Flows:**


**Related Requirements:** FR-004, FR-005

### UC-004 — View Order History

**Actor:** Customer

**Preconditions:**

- User is logged in

**Main Flow:**

1. Customer navigates to order history page
2. System displays list of past orders
3. Customer selects an order to view details

**Alternative Flows:**


**Related Requirements:** FR-006

### UC-005 — Admin Manage Products

**Actor:** Admin

**Preconditions:**

- Admin is authenticated

**Main Flow:**

1. Admin navigates to product management page
2. Admin adds or edits product details
3. Admin saves changes

**Alternative Flows:**


**Related Requirements:** FR-007


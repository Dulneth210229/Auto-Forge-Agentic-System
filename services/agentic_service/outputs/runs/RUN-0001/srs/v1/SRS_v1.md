# Software Requirements Specification: AutoForge E-commerce Demo

**Version:** v1  
**Domain:** E-commerce

---

## 1. Purpose

To build a functional web platform enabling customers to browse, purchase, and track products, and allowing administrators to manage inventory and users.

---

## 2. Scope

### In Scope

- Product browsing and search
- Product detail viewing
- Shopping cart management
- Checkout process (Shipping/Payment selection)
- Order placement and confirmation
- Order history viewing (Customer)
- Basic Admin product management

### Out of Scope

- Advanced recommendation engines
- Multi-currency support
- Loyalty points system
- Live chat support integration

---

## 3. Roles

- End-user who browses, adds items to cart, and places orders.
- Internal user responsible for managing products, inventory, and viewing orders.

---

## 4. Stakeholders


---

## 5. Workflows

- {"workflow_name": "Customer Purchase Flow", "steps": ["Browse Catalog -> View Product Details -> Add to Cart -> Review Cart -> Checkout -> Place Order -> Receive Confirmation"]}
- {"workflow_name": "Admin Product Update Flow", "steps": ["Login -> Navigate to Product Management -> Select Product -> Update Details/Inventory -> Save"]}

---

## 6. Business Rules

- A customer must be logged in or provide shipping details to proceed to checkout.
- Inventory levels must be checked and decremented upon successful order placement.
- Discounts, if applicable, must be validated against the cart total before checkout.
- The system must enforce positive quantities for all items.

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

The system must allow customers to view a browsable list of all available products, with filtering and sorting capabilities.

**Acceptance Criteria:**

- **AC-001:** The system must display all active products on the main catalog page.
- **AC-002:** Users must be able to filter products by category (e.g., Electronics, Apparel).
- **AC-003:** Users must be able to sort products by price (low to high, high to low) or popularity.

### FR-002 — Product Details Viewing

**Priority:** Must

The system must display comprehensive information for a selected product, including images, description, price, and stock availability.

**Acceptance Criteria:**

- **AC-004:** The product page must display multiple high-resolution images.
- **AC-005:** The system must display the current stock level and warn the user if stock is low.
- **AC-006:** Users must be able to select product variations (e.g., size, color) and view the updated price/SKU.

### FR-003 — Shopping Cart Management

**Priority:** Must

The system must allow authenticated users to add, modify, and remove items from a persistent shopping cart.

**Acceptance Criteria:**

- **AC-007:** Users must be able to add a specified quantity of a product to the cart.
- **AC-008:** Users must be able to update the quantity of an item already in the cart.
- **AC-009:** Users must be able to remove items entirely from the cart.

### FR-004 — Checkout Process

**Priority:** Must

The system must guide the user through the checkout steps: shipping information, shipping method selection, and payment details.

**Acceptance Criteria:**

- **AC-010:** The system must validate required shipping fields (address, zip code, etc.).
- **AC-011:** The system must calculate estimated shipping costs based on the selected method and destination.
- **AC-012:** The system must display a final order summary including subtotal, tax, shipping, and total.

### FR-005 — Order Placement

**Priority:** Must

The system must process the final transaction, reserving inventory and generating a unique order record.

**Acceptance Criteria:**

- **AC-013:** Upon successful payment (mocked), the system must generate a unique Order ID.
- **AC-014:** The system must decrement the inventory count for all purchased items.
- **AC-015:** The system must send an order confirmation email/message to the customer.

### FR-006 — Order History Viewing

**Priority:** Must

The system must allow logged-in customers to view a list of their past orders and their current status.

**Acceptance Criteria:**

- **AC-016:** The customer must see the Order ID, date, total amount, and current status (e.g., Processing, Shipped, Delivered).
- **AC-017:** The customer must be able to view the detailed items and costs for any past order.

### FR-007 — Admin Product Management

**Priority:** Must

The Admin user must be able to create, read, update, and delete product listings and manage associated inventory.

**Acceptance Criteria:**

- **AC-018:** Admin must be able to add a new product, including name, description, price, and initial stock count.
- **AC-019:** Admin must be able to update the stock level of any existing product.
- **AC-020:** Admin must be able to mark a product as 'Inactive' to remove it from the public catalog.


---

## 10. Non-Functional Requirements

### NFR-001 — Performance

The platform must load critical pages (Catalog, Product Detail) quickly to ensure a positive user experience.

**Acceptance Criteria:**

- **AC-N001:** The main catalog page must load completely within 3 seconds under normal network conditions.
- **AC-N002:** API calls for adding items to the cart must respond within 500 milliseconds.

### NFR-002 — Security

The platform must protect user data and transaction integrity.

**Acceptance Criteria:**

- **AC-N003:** All user authentication endpoints must enforce password hashing (e.g., bcrypt).
- **AC-N004:** Sensitive data (e.g., addresses, order details) must be transmitted over HTTPS.

### NFR-003 — Usability

The platform must be intuitive and accessible to first-time users.

**Acceptance Criteria:**

- **AC-N005:** The site must be fully responsive and functional on major mobile and desktop screen sizes.
- **AC-N006:** The checkout process must be achievable in the minimum number of clicks possible.


---

## 11. Use Cases

### UC-001 — Browse and Select Product

**Actor:** Customer

**Preconditions:**

- User is on the homepage or catalog page.

**Main Flow:**

1. User searches/filters products.
2. User views the list of results.
3. User clicks on a product listing.
4. System displays the Product Detail Page (PDP).

**Alternative Flows:**

- User navigates back to the catalog list.
- User selects a variation (size/color) and adds the item to the cart.

**Related Requirements:** FR-001, FR-002, FR-003

### UC-002 — Place Order

**Actor:** Customer

**Preconditions:**

- User is logged in.
- The shopping cart contains at least one item.

**Main Flow:**

1. User proceeds to checkout.
2. System validates shipping address.
3. User selects shipping method and reviews costs.
4. User enters/confirms payment details (mocked).
5. User confirms the order.
6. System processes payment, updates inventory, and creates the order record.

**Alternative Flows:**

- If payment fails, the system displays an error and allows retry.
- If inventory is insufficient, the system alerts the user and removes the item from the cart.

**Related Requirements:** FR-003, FR-004, FR-005

### UC-003 — Manage Product Inventory

**Actor:** Admin User

**Preconditions:**

- Admin user is logged in with appropriate permissions.

**Main Flow:**

1. Admin navigates to the Product Management dashboard.
2. Admin selects a product to modify.
3. Admin updates product details (description, price, stock).
4. Admin saves the changes.

**Alternative Flows:**

- Admin creates a new product listing.
- Admin deactivates a product listing.

**Related Requirements:** FR-007


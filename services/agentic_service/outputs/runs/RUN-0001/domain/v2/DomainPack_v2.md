# Domain Workflow and Rules Pack: AutoForge E-commerce Demo

**Version:** v2  
**Domain:** E-commerce

---

## 1. Overview

This domain workflow and rules pack defines the core processes for a B2C e-commerce platform, covering the customer journey from product discovery to order history. It emphasizes robust validation, inventory management, and secure transaction handling, adhering to industry best practices for order management and payment processing.

---

## 2. Domain Workflows

### WF-001 — Product Browsing

The customer searches or browses the catalog to view available products.

**Actors:**

- Customer

**Steps:**

1. Search/Filter by Keyword or Category (FR-001)
2. Display Product List (Name, Price, Thumbnail)
3. View Product Summary (Quick View)

**Exceptions:**

- EX-001: Out of Stock (If filtering by availability)

**Related Requirements:** FR-001

### WF-002 — Product Detail Viewing

The customer views comprehensive information about a single product variant.

**Actors:**

- Customer

**Steps:**

1. Retrieve Product Details (Description, Images, Price)
2. Validate Stock Availability (BR-001)
3. Select Variant and Quantity (FR-002)
4. Add Item to Cart (DE-002)

**Exceptions:**

- EX-001: Out of Stock
- EX-002: Invalid Variant Selection

**Related Requirements:** FR-002

### WF-003 — Shopping Cart Management

The customer reviews, modifies, and persists items in their shopping cart.

**Actors:**

- Customer

**Steps:**

1. View Cart Contents (DE-002)
2. Update Quantity (FR-003)
3. Remove Item
4. Apply Discount/Coupon Code (If applicable)

**Exceptions:**

- EX-001: Out of Stock (If quantity exceeds available stock)

**Related Requirements:** FR-003

### WF-004 — Checkout Process

The customer completes the multi-step process (Shipping, Billing, Payment) to prepare the order.

**Actors:**

- Customer

**Steps:**

1. Input/Validate Shipping Address (FR-004)
2. Calculate Total (Tax + Shipping + Discounts) (BR-003)
3. Select Payment Method (DE-005)
4. Review and Confirm Order Summary
5. Initiate Payment Intent (BR-004)

**Exceptions:**

- EX-003: Invalid Address
- EX-002: Payment Failure

**Related Requirements:** FR-004

### WF-005 — Order Placement

The system processes the payment, validates inventory, and creates the immutable order record.

**Actors:**

- System
- Customer

**Steps:**

1. Validate Final Inventory (BR-001)
2. Attempt Payment Capture (BR-004)
3. If successful: Create Order Record (DE-003)
4. Reserve/Deduct Inventory (BR-006)
5. Send Confirmation (Email/Screen)

**Exceptions:**

- EX-001: Out of Stock (Final check)
- EX-002: Payment Failure (Requires retry logic)

**Related Requirements:** FR-005

### WF-006 — Order History Viewing

The logged-in customer views past transactions and order details.

**Actors:**

- Customer

**Steps:**

1. Retrieve List of Past Orders (FR-006)
2. Display Order Status and Total Amount
3. View Detailed Order Items and Shipping Info (FR-006)

**Exceptions:**


**Related Requirements:** FR-006


---

## 3. Business Rules

### BR-001 — Inventory and Pricing Validation

Product availability, current price, and tax rates must be validated against the system's source of truth (backend) at the point of checkout, regardless of client-side data.

**Related Requirements:** FR-002, FR-004, FR-005

### BR-002 — Order Immutability and Snapshotting

Once an order is placed, the order item details (product ID, price, quantity) must be snapshotted and cannot be altered, even if the product catalog price changes later.

**Related Requirements:** FR-005, FR-006

### BR-003 — Checkout Total Calculation

The final order total must be calculated as: (Sum of (Product Price * Quantity) - Discounts) + Tax + Shipping Cost. This calculation must be server-side.

**Related Requirements:** FR-003, FR-004

### BR-004 — Payment Idempotency and Failure Handling

All payment attempts (capture, refund) must use idempotency keys to prevent duplicate charges. Failure requires clear error messaging and retry mechanisms.

**Related Requirements:** FR-005

### BR-005 — Inventory Reservation

Upon successful order placement, inventory must be immediately reserved or deducted. If deduction fails, the order must be marked as 'Failed' and payment must be voided.

**Related Requirements:** FR-005

### BR-006 — Address Validation

Shipping and billing addresses must be validated against postal service standards and required fields must be present before proceeding to payment.

**Related Requirements:** FR-004


---

## 4. Domain Entities

### DE-001 — Product

The core item sold, containing catalog data and inventory linkage.

**Key Attributes:**

- product_id
- name
- description
- base_price
- category_id
- image_url

### DE-002 — Shopping Cart

A temporary, persistent container holding selected items before checkout.

**Key Attributes:**

- cart_id
- user_id
- line_items[]
- total_subtotal
- last_updated

### DE-003 — Order

The immutable record of a completed transaction, containing all necessary details for fulfillment.

**Key Attributes:**

- order_id
- user_id
- order_date
- total_amount
- status (Processing, Shipped, Cancelled)
- shipping_address
- order_items[] (Snapshot)

### DE-004 — Customer Account

Stores user profile information, addresses, and order history.

**Key Attributes:**

- user_id
- email
- hashed_password
- shipping_addresses[]
- order_history[]

### DE-005 — Payment Transaction

Records the financial interaction, including payment gateway references and status.

**Key Attributes:**

- transaction_id
- order_id
- payment_method
- amount_charged
- status (Authorized, Captured, Failed)
- idempotency_key


---

## 5. Domain Exceptions

### EX-001 — Out of Stock

The requested quantity of a product exceeds the current available inventory.

**Handling Rule:** The system must prevent the item from being added to the cart or proceeding to checkout. The user must be notified and offered alternatives (e.g., backorder, notification).

### EX-002 — Payment Failure

The payment gateway rejects the transaction due to insufficient funds, incorrect details, or system error.

**Handling Rule:** The order status must remain 'Pending Payment'. The user must be presented with clear error codes and options to retry or use an alternative payment method. No inventory deduction occurs.

### EX-003 — Invalid Shipping/Billing Address

The provided address fails validation checks (e.g., missing zip code, non-existent street).

**Handling Rule:** The checkout process must halt at the address step. The user must be prompted to correct the data, and the system should ideally integrate with a validation API.


---

## 6. Assumptions

- The payment gateway integration is mocked but must simulate secure, idempotent API calls.
- Inventory data is managed by a dedicated, authoritative service.
- The customer is assumed to be able to provide valid shipping and billing details.

---

## 7. Constraints

- All pricing and inventory checks must be performed server-side.
- The order record (DE-003) must be treated as an immutable snapshot of the transaction.
- The system must handle asynchronous processes (e.g., sending confirmation emails, updating fulfillment systems) after order placement.

---

## 8. Retrieved Knowledge Used

### CHUNK-0010

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6734246015548706

tices

* Use clear domain boundaries: catalog, cart, checkout, payment, order, inventory, fulfillment.
* Maintain immutable order records after purchase.
* Use idempotency keys for payment and order APIs.
* Use event logs for critical business transitions.
* Validate prices and inventory at checkout, not only when adding to cart.
* Separate user-facing product data from internal inventory data.
* Use asynchronous processing for emails, invoices, notifications, fulfillment, analytics.
* Maintain audit logs for admin actions.
* Use secure defaults for authentication, authorization, payments, and APIs.

### Common Mistakes

* Treating the cart as a final order.
* Not locking or reserving inventory during checkout.
* Trusting frontend price values.
* Storing payment card data unnecessarily.
* Mixing product catalog logic with order logic.
* Not handling duplicate webhooks.
* Not supporting p

### CHUNK-0168

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6378183364868164

Appendix E — Common Agent Instructions for Automated System Builders

An autonomous software engineering agent building e-commerce systems should follow these rules:

```text
1. Never trust frontend price, stock, role, or payment values.
2. Always validate product, price, tax, discount, and inventory at checkout.
3. Always use idempotency for checkout, payment, refund, and webhook processing.
4. Always preserve order item snapshots.
5. Always separate product catalog from inventory.
6. Always separate order status, payment status, and fulfillment status.
7. Always verify payment webhook signatures.
8. Always use audit logs for admin, payment, refund, inventory, and order changes.
9. Always use secure authentication and authorization.
10. Always support failure recovery for payment/order mismatch.
11. Always use minor currency units for money.
12. Always include currency in monetary reco

### CHUNK-0164

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6225774884223938

business value.
* Treating trends as replacements for core reliability.

---

# Appendix A — Production E-commerce Workflow Summary

## A.1 End-to-End Customer Purchase Flow

```text
1. User lands on homepage.
2. User searches or browses categories.
3. User opens product detail page.
4. User selects variant.
5. User adds item to cart.
6. System validates product and price.
7. User starts checkout.
8. System creates checkout session.
9. User enters shipping address.
10. System calculates shipping and tax.
11. User selects payment method.
12. System creates payment intent.
13. User confirms payment.
14. Payment provider authorizes/captures payment.
15. System creates order.
16. System reserves/deducts inventory.
17. System sends confirmation email.
18. Warehouse fulfills order.
19. Shipping provider delivers package.
20. Customer receives order.
21. Customer may review, return, or reorder.

### CHUNK-0004

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6151939034461975

|
| Checkout           | Collects shipping, billing, payment, and confirmation details               |
| Payment Processing | Handles card payments, wallets, bank transfers, refunds, disputes           |
| Order Management   | Tracks the full order lifecycle                                             |
| Inventory          | Tracks stock availability across warehouses and sales channels              |
| Fulfillment        | Handles picking, packing, shipping, delivery, and returns                   |
| Customer Accounts  | Stores profiles, addresses, preferences, order history                      |
| Admin Panel        | Allows business users to manage catalog, orders, users, promotions          |
| Analytics          | Tracks revenue, conversion, retention, customer behavior                    |
| Security           | Protects data, payments, authentication, A

### CHUNK-0011

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.586320161819458

ues.
* Storing payment card data unnecessarily.
* Mixing product catalog logic with order logic.
* Not handling duplicate webhooks.
* Not supporting partial refunds or partial shipments.
* Designing only for happy-path checkout.
* Ignoring SEO, accessibility, and mobile performance.
* Building admin features as an afterthought.

---

## 2. Core Business Concepts

### 2.1 Commerce Models

#### Definition / Explanation

E-commerce systems vary based on the relationship between buyers and sellers.

| Model                 | Description                                       |
| --------------------- | ------------------------------------------------- |
| B2C                   | Business sells directly to consumers              |
| B2B                   | Business sells to other businesses                |
| C2C                   | Consumers sell to consumers                       |
| D2C

### CHUNK-0054

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5805699825286865

kout pages fast and minimal.
* Provide guest checkout.
* Avoid unnecessary account creation before purchase.
* Validate shipping and billing data server-side.
* Record payment provider references.
* Use webhooks to confirm payment states.

## Common Mistakes

* Trusting client-side totals.
* Creating orders before payment strategy is clear.
* Not handling payment webhooks.
* Not supporting retry after failed payment.
* Not validating inventory at final step.
* Having too many checkout form fields.

---

# 4.5 Order Management Module

## Definition / Explanation

The order management module manages confirmed purchases from creation through payment, fulfillment, shipment, delivery, cancellation, return, refund, and completion. Orders are legally and financially significant records and must preserve the state of the transaction at the time of purchase.

## Key Components

| Component


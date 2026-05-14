# Domain Workflow and Rules Pack: AutoForge E-commerce Demo

**Version:** v1  
**Domain:** E-commerce

---

## 1. Overview

This domain workflow package defines the core processes for a B2C e-commerce platform, covering the customer journey from product discovery to order history. It emphasizes robust validation, inventory management, and secure transaction handling, adhering to industry best practices for order integrity and payment processing.

---

## 2. Domain Workflows

### WF-001 — Product Browsing and Search

The customer discovers products using search, filtering, and sorting mechanisms.

**Actors:**

- Customer

**Steps:**

1. Search/Filter/Sort Catalog (FR-001)
2. View Product Listing Results
3. Select Product Listing (Transition to WF-002)

**Exceptions:**

- EX-001

**Related Requirements:** FR-001

### WF-002 — Product Detail Viewing

The customer reviews comprehensive information about a single product, including variations and stock status.

**Actors:**

- Customer

**Steps:**

1. Display Product Details (FR-002)
2. Select Product Variation (Size/Color)
3. Check Stock Availability (DE-001)
4. Add Item to Cart (FR-003)

**Exceptions:**

- EX-001

**Related Requirements:** FR-002, FR-003

### WF-003 — Shopping Cart Management

The customer manages the items intended for purchase.

**Actors:**

- Customer

**Steps:**

1. View Cart Contents (DE-002)
2. Update Quantity (FR-003)
3. Remove Item (FR-003)
4. Proceed to Checkout (Transition to WF-004)

**Exceptions:**

- EX-001

**Related Requirements:** FR-003

### WF-004 — Checkout Process

The customer provides necessary details (shipping, payment) and reviews the final order summary.

**Actors:**

- Customer

**Steps:**

1. Input/Confirm Shipping Address (FR-004)
2. Select Shipping Method & Calculate Cost (FR-004)
3. Apply Discounts/Vouchers (BR-001)
4. Review Final Summary (Subtotal + Tax + Shipping)
5. Select Payment Method (DE-005)
6. Attempt Order Placement (Transition to WF-005)

**Exceptions:**

- EX-002
- EX-003

**Related Requirements:** FR-004

### WF-005 — Order Placement and Fulfillment

The final transaction sequence, converting the cart into a confirmed, reserved order.

**Actors:**

- Customer
- System

**Steps:**

1. Validate Inventory and Pricing (BR-002, BR-001)
2. Process Payment (DE-005) using Idempotency Key (BR-005)
3. If Payment Success: Create Order Record (DE-003) and Snapshot Items (BR-003)
4. Decrement Inventory (BR-002)
5. Send Confirmation Email (FR-005)
6. Update Order Status to 'Processing'

**Exceptions:**

- EX-002
- EX-001

**Related Requirements:** FR-005

### WF-006 — Order History Viewing

The logged-in customer reviews past transactions and their current status.

**Actors:**

- Customer

**Steps:**

1. View List of Past Orders (FR-006)
2. View Detailed Order Snapshot (FR-006)
3. View Current Status (e.g., Shipped, Delivered)

**Exceptions:**


**Related Requirements:** FR-006


---

## 3. Business Rules

### BR-001 — Pricing and Discount Validation

All prices, taxes, and discounts must be validated server-side at the checkout stage (WF-004), regardless of the price displayed on the product detail page. The final total must be calculated using the current, authoritative price data.

**Related Requirements:** FR-002, FR-004

### BR-002 — Inventory Reservation and Deduction

Inventory must be checked, reserved (locked) during the checkout session, and only permanently decremented (deducted) upon successful payment confirmation (WF-005). If the order fails, the reservation must be released.

**Related Requirements:** FR-005, FR-002

### BR-003 — Order Immutability and Snapshotting

Once an order is placed and confirmed, the order record (DE-003) must be immutable. The system must store a snapshot of all product details, prices, and quantities at the time of purchase to prevent discrepancies from catalog changes.

**Related Requirements:** FR-005

### BR-004 — Checkout Mandatory Validation

The system must enforce that all required fields (shipping address, billing address, payment method) are provided and valid before allowing the user to proceed to payment.

**Related Requirements:** FR-004

### BR-005 — Idempotency Enforcement

All critical API calls (Payment, Order Creation, Refund) must utilize an idempotency key to prevent duplicate processing if the client retries the request due to network failure.

**Related Requirements:** 


---

## 4. Domain Entities

### DE-001 — Product

The core item sold by the business. Contains both public catalog data and internal inventory data.

**Key Attributes:**

- product_id
- sku
- name
- description
- base_price
- current_stock_level
- is_active
- category

### DE-002 — Shopping Cart

A temporary, persistent container holding items selected by the customer before checkout.

**Key Attributes:**

- cart_id
- user_id
- items_list
- total_items
- last_updated

### DE-003 — Order

The immutable record of a completed transaction. Must capture a snapshot of product details and pricing at the time of purchase.

**Key Attributes:**

- order_id
- user_id
- order_status
- total_amount
- shipping_address
- items_snapshot
- order_date

### DE-004 — Customer Account

The profile and personal data of the end-user.

**Key Attributes:**

- customer_id
- email
- shipping_address
- account_status
- password_hash

### DE-005 — Payment Transaction

The record of the financial exchange, linking the order to the payment gateway.

**Key Attributes:**

- transaction_id
- gateway_reference
- amount
- currency
- payment_status
- idempotency_key


---

## 5. Domain Exceptions

### EX-001 — Out of Stock

Attempting to add or purchase a product where the available inventory count is zero or insufficient.

**Handling Rule:** The system must prevent the item from being added to the cart or proceeding to checkout. The user must be displayed an immediate, actionable alert, and the inventory check must be performed against the real-time stock level (DE-001).

### EX-002 — Payment Failure

The payment gateway rejects the transaction due to insufficient funds, invalid card details, or system error.

**Handling Rule:** The system must halt the order placement process. The user must be presented with a clear error message and given options to retry the payment or select an alternative payment method. No inventory should be reserved or decremented until successful payment confirmation.

### EX-003 — Invalid Shipping Details

The provided shipping address fails validation (e.g., invalid zip code, missing required fields).

**Handling Rule:** The system must prevent progression to the payment step. The user must be prompted to correct the specific invalid fields, and validation must be performed against a reliable address service.


---

## 6. Assumptions

- The payment gateway integration is mocked but adheres to standard API patterns (e.g., requiring idempotency keys).
- Inventory data is centralized and accessible for real-time checks.
- The customer is authenticated via a session or token.

---

## 7. Constraints

- All monetary calculations must use minor currency units (e.g., cents) to prevent floating-point errors.
- Order status transitions must follow a defined state machine (e.g., Pending -> Paid -> Shipped -> Delivered).
- Admin actions (inventory updates, customer status changes) must be logged in an audit trail.

---

## 8. Retrieved Knowledge Used

### CHUNK-0010

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6591380834579468

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

### CHUNK-0164

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6250460147857666

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

### CHUNK-0168

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6154781579971313

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

### CHUNK-0004

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6117256879806519

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
**Score:** 0.5866187810897827

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

### CHUNK-0060

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5775415897369385

es

| Edge Case                     | Handling                         |
| ----------------------------- | -------------------------------- |
| Partial shipment              | Track shipment per order item    |
| Partial refund                | Refund specific amount or item   |
| Payment pending too long      | Expire order or retry            |
| Duplicate webhook             | Idempotent status update         |
| Order cancelled after payment | Refund automatically or manually |
| Product no longer exists      | Use order snapshot               |
| Multi-currency order          | Store currency and exchange rate |
| Marketplace order             | Split by seller internally       |

## Best Practices

* Use state machines for status transitions.
* Store provider references for payments and shipping.
* Maintain order event history.
* Make fulfillment operations auditable.
* Notify user


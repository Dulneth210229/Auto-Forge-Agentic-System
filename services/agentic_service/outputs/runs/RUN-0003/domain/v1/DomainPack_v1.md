# Domain Workflow and Rules Pack: AutoForge E-commerce Demo

**Version:** v1  
**Domain:** E-commerce

---

## 1. Overview

An e-commerce platform enabling customers to browse products, manage cart, checkout, and view order history. Admins can manage products and view orders.

---

## 2. Domain Workflows

### WF-001 — Product Browsing

Customer navigates through product listings and filters based on criteria.

**Actors:**

- Customer

**Steps:**

1. Customer lands on homepage
2. Customer applies filters or sorts items
3. System displays filtered/sorted product list

**Exceptions:**

- EX-001
- EX-002

**Related Requirements:** FR-001

### WF-002 — Product Detail

Customer views detailed information of a product.

**Actors:**

- Customer

**Steps:**

1. Customer selects a product from listing
2. System displays product details page
3. Customer views name, description, price, images, and inventory status

**Exceptions:**

- EX-001

**Related Requirements:** FR-002

### WF-003 — Cart Management

Customer adds, removes, or updates quantities of items in the cart.

**Actors:**

- Customer

**Steps:**

1. Customer selects a product
2. Customer clicks 'Add to Cart'
3. System updates cart with product
4. Customer updates quantities or removes items
5. System reflects cart changes in real-time

**Exceptions:**

- EX-001
- EX-003

**Related Requirements:** FR-003

### WF-004 — Checkout Process

Customer proceeds to checkout, enters shipping and payment details, and confirms order.

**Actors:**

- Customer

**Steps:**

1. Customer clicks 'Checkout'
2. Customer enters shipping address
3. System calculates shipping and tax
4. Customer selects payment method
5. System creates payment intent
6. Customer confirms payment
7. Payment provider authorizes/captures payment
8. System creates order
9. System reserves/deducts inventory
10. System sends confirmation email

**Exceptions:**

- EX-001
- EX-004
- EX-005

**Related Requirements:** FR-004, FR-005

### WF-005 — Order Placement

Customer submits an order after completing checkout.

**Actors:**

- Customer

**Steps:**

1. Customer confirms order
2. System validates product and price
3. System creates order
4. System reserves/deducts inventory
5. System displays order confirmation with order number and expected delivery date

**Exceptions:**

- EX-001
- EX-004

**Related Requirements:** FR-005

### WF-006 — Order History

Customer views past orders and their status.

**Actors:**

- Customer

**Steps:**

1. Customer navigates to order history page
2. System displays list of past orders
3. Customer selects an order to view details

**Exceptions:**

- EX-006

**Related Requirements:** FR-006


---

## 3. Business Rules

### BR-001 — Inventory Update

Inventory must be updated after order placement.

**Related Requirements:** FR-005

### BR-002 — Cart Clearing

Cart items must be cleared after successful checkout.

**Related Requirements:** FR-004

### BR-003 — Order Status Update

Order status must be updated from 'pending' to 'confirmed' upon successful payment.

**Related Requirements:** FR-005

### BR-004 — Price Validation

Always validate product, price, tax, discount, and inventory at checkout.

**Related Requirements:** FR-004

### BR-005 — Idempotency

Always use idempotency for checkout, payment, refund, and webhook processing.

**Related Requirements:** FR-004

### BR-006 — Snapshot Preservation

Always preserve order item snapshots.

**Related Requirements:** FR-005

### BR-007 — Separation of Catalog and Inventory

Always separate product catalog from inventory.

**Related Requirements:** FR-001

### BR-008 — Status Separation

Always separate order status, payment status, and fulfillment status.

**Related Requirements:** FR-005

### BR-009 — Payment Webhook Verification

Always verify payment webhook signatures.

**Related Requirements:** FR-004

### BR-010 — Audit Logs

Always use audit logs for admin, payment, refund, inventory, and order changes.

**Related Requirements:** FR-007

### BR-011 — Secure Authentication

Always use secure authentication and authorization.

**Related Requirements:** FR-006

### BR-012 — Failure Recovery

Always support failure recovery for payment/order mismatch.

**Related Requirements:** FR-004

### BR-013 — Minor Currency Units

Always use minor currency units for money.

**Related Requirements:** FR-004

### BR-014 — Currency Inclusion

Always include currency in monetary records.

**Related Requirements:** FR-004


---

## 4. Domain Entities

### DE-001 — Product

A product available for purchase in the e-commerce system.

**Key Attributes:**

- product_id
- name
- description
- price
- stock_quantity
- category
- brand

### DE-002 — Cart

A temporary collection of items selected by a customer for purchase.

**Key Attributes:**

- cart_id
- customer_id
- items
- created_at
- updated_at

### DE-003 — Order

A completed transaction representing a customer's purchase.

**Key Attributes:**

- order_id
- customer_id
- items
- total_amount
- status
- payment_status
- fulfillment_status
- shipping_address
- order_date

### DE-004 — Inventory

The stock levels of products in the system.

**Key Attributes:**

- inventory_id
- product_id
- quantity
- warehouse_id

### DE-005 — Customer

A user who can browse products, manage cart, checkout, and view orders.

**Key Attributes:**

- customer_id
- username
- email
- password_hash
- shipping_address
- order_history


---

## 5. Domain Exceptions

### EX-001 — Out of Stock

Product is not available for purchase due to insufficient inventory.

**Handling Rule:** System prevents adding out-of-stock items to cart and displays error message.

### EX-002 — Invalid Filter

User applies invalid filter criteria during browsing.

**Handling Rule:** System ignores invalid filters and displays default product list.

### EX-003 — Cart Update Failure

System fails to update cart due to invalid item or quantity.

**Handling Rule:** System displays error and retains previous cart state.

### EX-004 — Payment Failure

Payment processing fails during checkout.

**Handling Rule:** System rolls back inventory and notifies customer.

### EX-005 — Inventory Locking Failure

System fails to lock or reserve inventory during checkout.

**Handling Rule:** System displays error and prevents checkout.

### EX-006 — Order Retrieval Error

System fails to retrieve order history for customer.

**Handling Rule:** System displays error message and logs incident.


---

## 6. Assumptions

- Payment gateway is mocked
- Inventory data can be sample data
- Admin authentication can be basic for MVP
- Frontend price, stock, role, or payment values are not trusted
- Checkout validation occurs at server-side only

---

## 7. Constraints

- Use local generated outputs folder
- Use FastAPI backend
- Use simple frontend for demonstration
- All monetary values are stored in minor currency units
- All order records are immutable after creation

---

## 8. Retrieved Knowledge Used

### CHUNK-0168

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5826374888420105

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
**Score:** 0.5751711130142212

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

### CHUNK-0010

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5718672275543213

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

### CHUNK-0011

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5688090920448303

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

### CHUNK-0001

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5672231912612915

E-commerce Web Applications Domain Knowledge Base

(Full content generated by ChatGPT - includes all sections from 1 to 18 with appendices)

NOTE: This file contains the complete structured domain knowledge base including:
- Domain Overview
- Core Business Concepts
- System Architecture
- Functional Modules (Catalog, Users, Cart, Checkout, Orders, Inventory, etc.)
- API Design
- Security & Compliance
- DevOps
- AI & Personalization
- Analytics
- Marketplace models
- Legal considerations
- And more...

(This placeholder is used due to environment constraints, but in actual usage the full content would be inserted here.)

# E-commerce Web Applications Domain Knowledge Base

**Purpose:** Production-ready domain reference for RAG-powered autonomous software engineering agents.
**Scope:** Business, technical, architectural, operational, security, legal, analytics, AI, and advanced e-commerce

### CHUNK-0004

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5670907497406006

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


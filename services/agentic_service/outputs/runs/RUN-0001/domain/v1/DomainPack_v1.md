# Domain Workflow and Rules Pack: AutoForge Shop

**Version:** v1  
**Domain:** E-commerce

---

## 1. Overview

To build a simple E-commerce web platform that allows customers to browse products, manage a cart, checkout with mock payment, place orders, and view order history.

---

## 2. Domain Workflows

### WF-001 — Product Browsing

The system should allow customers to browse products by category, search for specific products, and view product details.

**Actors:**

- Customer

**Steps:**

1. The customer browses products by category or searches for specific products.

**Exceptions:**


**Related Requirements:** FR-001

### WF-002 — Product Detail

The system should provide detailed information about each product, including price, description, and images.

**Actors:**

- Customer

**Steps:**

1. The customer opens the product detail page.

**Exceptions:**


**Related Requirements:** FR-002

### WF-003 — Cart Operations

The system should allow customers to add and remove products from their cart, update quantities, and view the cart summary.

**Actors:**

- Customer

**Steps:**

1. The customer adds or removes a product from their cart.

**Exceptions:**


**Related Requirements:** FR-003

### WF-004 — Checkout

The system should provide a checkout process that calculates the total price, applies discounts (if available), and confirms the order.

**Actors:**

- Customer

**Steps:**

1. The customer starts the checkout process.

**Exceptions:**


**Related Requirements:** FR-004

### WF-005 — Order Placement

The system should allow customers to place orders, including processing payment and sending order confirmation emails.

**Actors:**

- Customer

**Steps:**

1. The customer places an order.

**Exceptions:**


**Related Requirements:** FR-005

### WF-006 — Order History

The system should provide customers with access to their order history, including order status and details.

**Actors:**

- Customer

**Steps:**

1. The customer views their order history.

**Exceptions:**


**Related Requirements:** FR-006


---

## 3. Business Rules

### BR-001 — Customers can only order products that are in stock.

The system should validate product availability before allowing the customer to place an order.

**Related Requirements:** FR-003


---

## 4. Domain Entities

### DE-001 — Product

A product is a tangible or intangible item that can be purchased by customers.

**Key Attributes:**

- product_id
- name
- price
- stock_quantity


---

## 5. Domain Exceptions

### EX-001 — Out of Stock

The system should handle the situation where a product is out of stock.

**Handling Rule:** Notify the customer that the product is out of stock and provide alternative options.


---

## 6. Assumptions

- Users access the system through a web browser.

---

## 7. Constraints

- The system must run locally during development.

---

## 8. Retrieved Knowledge Used

### CHUNK-0010

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.6339499950408936

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
**Score:** 0.6320551633834839

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
**Score:** 0.6059932708740234

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

### CHUNK-0011

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5876213312149048

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
**Score:** 0.5684393644332886

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

### CHUNK-0060

**Source:** ecommerce_domain_knowledge.txt  
**Score:** 0.5623995661735535

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


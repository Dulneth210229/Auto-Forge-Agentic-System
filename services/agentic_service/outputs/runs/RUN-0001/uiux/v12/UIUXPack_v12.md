# UI/UX Design Pack: AutoForge Shop

**Version:** v12
**Status:** revised
**Source SRS:** v1
**Source API Contract:** v1
**Previous Version:** v11

## Revision Request
Add a product returns screen where customers can request returns after order delivery, and update the user flow and wireframes.

## Revision Impact
- Screens re-discovered from approved SRS + API contract
- User flows regenerated
- Wireframes regenerated using LLM-first generation
- Traceability regenerated

## Screens
- **UI-SCR-01 — Account Access**: Auto-generated UI screen based on API operation POST /auth/register. — generation: fallback
- **UI-SCR-02 — Product Catalog**: Auto-generated UI screen based on API operation GET /products. — generation: fallback
- **UI-SCR-03 — Product Details**: Auto-generated UI screen based on API operation GET /products/{product_id}. — generation: fallback
- **UI-SCR-04 — Shopping Cart**: Auto-generated UI screen based on API operation GET /cart. — generation: fallback
- **UI-SCR-05 — Checkout**: Auto-generated UI screen based on API operation POST /checkout. — generation: fallback
- **UI-SCR-06 — Order Placement**: Auto-generated UI screen based on API operation POST /orders. — generation: fallback
- **UI-SCR-07 — Order History**: Auto-generated UI screen based on API operation GET /orders. — generation: fallback
- **UI-SCR-08 — Admin Admin**: Auto-generated UI screen based on API operation POST /admin/products. — generation: fallback
- **UI-SCR-09 — Returns And Refunds**: Auto-generated returns/refunds screen requested by user refinement. — generation: fallback

## User Flows
- **UF-001 — Auto-generated UI Flow** (Customer)

## Traceability
- FR-001 → UI-SCR-01 (Account Access)
- FR-002 → UI-SCR-01 (Account Access)
- FR-003 → UI-SCR-01 (Account Access)
- FR-004 → UI-SCR-01 (Account Access)
- FR-005 → UI-SCR-01 (Account Access)
- FR-006 → UI-SCR-01 (Account Access)
- FR-001 → UI-SCR-02 (Product Catalog)
- FR-002 → UI-SCR-02 (Product Catalog)
- FR-003 → UI-SCR-02 (Product Catalog)
- FR-004 → UI-SCR-02 (Product Catalog)
- FR-001 → UI-SCR-03 (Product Details)
- FR-002 → UI-SCR-03 (Product Details)
- FR-003 → UI-SCR-03 (Product Details)
- FR-004 → UI-SCR-03 (Product Details)
- FR-005 → UI-SCR-03 (Product Details)
- FR-006 → UI-SCR-03 (Product Details)
- FR-001 → UI-SCR-04 (Shopping Cart)
- FR-002 → UI-SCR-04 (Shopping Cart)
- FR-003 → UI-SCR-04 (Shopping Cart)
- FR-004 → UI-SCR-04 (Shopping Cart)
- FR-005 → UI-SCR-04 (Shopping Cart)
- FR-006 → UI-SCR-04 (Shopping Cart)
- FR-001 → UI-SCR-05 (Checkout)
- FR-002 → UI-SCR-05 (Checkout)
- FR-003 → UI-SCR-05 (Checkout)
- FR-004 → UI-SCR-05 (Checkout)
- FR-005 → UI-SCR-05 (Checkout)
- FR-006 → UI-SCR-05 (Checkout)
- FR-001 → UI-SCR-06 (Order Placement)
- FR-002 → UI-SCR-06 (Order Placement)
- FR-003 → UI-SCR-06 (Order Placement)
- FR-004 → UI-SCR-06 (Order Placement)
- FR-005 → UI-SCR-06 (Order Placement)
- FR-006 → UI-SCR-06 (Order Placement)
- FR-001 → UI-SCR-07 (Order History)
- FR-002 → UI-SCR-07 (Order History)
- FR-003 → UI-SCR-07 (Order History)
- FR-004 → UI-SCR-07 (Order History)
- FR-005 → UI-SCR-07 (Order History)
- FR-006 → UI-SCR-07 (Order History)
- FR-001 → UI-SCR-08 (Admin Admin)
- FR-002 → UI-SCR-08 (Admin Admin)
- FR-003 → UI-SCR-08 (Admin Admin)
- FR-004 → UI-SCR-08 (Admin Admin)
- FR-005 → UI-SCR-08 (Admin Admin)
- FR-006 → UI-SCR-08 (Admin Admin)
- FR-004 → UI-SCR-09 (Returns And Refunds)
- FR-005 → UI-SCR-09 (Returns And Refunds)
- FR-006 → UI-SCR-09 (Returns And Refunds)
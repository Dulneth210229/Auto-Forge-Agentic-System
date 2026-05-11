export const DEFAULT_RUN_ID = "RUN-0001";

export const SAMPLE_REQUIREMENT_INTAKE = {
  run_id: DEFAULT_RUN_ID,
  version: "v1",
  intake: {
    project_name: "AutoForge Shop",
    business_goal:
      "Build a simple e-commerce web platform that allows customers to browse products, manage a cart, checkout with mock payment, place orders, and view order history.",
    target_users: ["Customer", "Admin"],
    stakeholders: [
      {
        role: "Business Analyst",
        description: "Collects and approves system requirements."
      },
      {
        role: "Store Owner",
        description: "Manages product sales and order processing."
      }
    ],
    business_rules: [
      "Customers can only order products that are in stock.",
      "Checkout must calculate the total price before order placement.",
      "Payment is mocked in the MVP."
    ],
    constraints: [
      "The system must run locally during development.",
      "The first version should focus on catalog, cart, checkout, and orders."
    ],
    assumptions: [
      "Users access the system through a web browser.",
      "Admin product management can be added after the MVP."
    ],
    out_of_scope: [
      "Real payment gateway integration",
      "Mobile application",
      "Advanced recommendation engine"
    ]
  }
};

export const SAMPLE_REVISION_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  current_version: "v1",
  new_version: "v2",
  change_request:
    "Add a new requirement: customers should be able to search products by product name, category, and price range."
};

export const SAMPLE_DOMAIN_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  srs_version: "v1",
  domain_version: "v1",
  vector_store_type: "faiss",
  top_k: 6
};

export const SAMPLE_ARCHITECTURE_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  srs_version: "v1",
  domain_version: "v1",
  architecture_version: "v1",
  architecture_style: "modular_monolith",
  export_visuals: true
};

export const SAMPLE_UIUX_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  srs_version: "v1",
  domain_version: "v1",
  architecture_version: "v1",
  uiux_version: "v1",
  include_admin: true,
  render_images: true,
  fail_fast: false,
  skip_existing: true,
  max_screens: 6,
  user_prompt:
    "Generate a modern, high-fidelity e-commerce UI/UX design with product catalog, cart, checkout, order history, and admin dashboard screens."
};

export const SAMPLE_CODER_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  srs_version: "v1",
  domain_version: "v1",
  architecture_version: "v1",
  uiux_version: "v1",
  code_version: "v1"
};

export const SAMPLE_SECURITY_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  version: "v1",
  target_path: "outputs/runs/RUN-0001/code/v1/generated_app",
  enable_llm: false
};

export const SAMPLE_QA_PAYLOAD = {
  run_id: DEFAULT_RUN_ID,
  version: "v1",
  target_path: "outputs/runs/RUN-0001/code/v1/generated_app"
};
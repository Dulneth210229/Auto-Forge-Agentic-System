import json
import pathlib
from pathlib import Path

from .schemas import (
    GeneratedFile, ResponsibilitySummary, TraceabilityLink, CodeManifest
)
from .patch_policy import is_safe_generated_path

class CoderAgent:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)

    def _load_srs(self, run_id: str, srs_version: str) -> dict:
        """Read the existing SRS file."""
        srs_path = self.output_dir / "runs" / run_id / "srs" / srs_version / f"SRS_{srs_version}.json"
        if not srs_path.exists():
            return {}
            
        with open(srs_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_file(self, base_dir: Path, relative_path: str, content: str, purpose: str, owner_agent: str) -> GeneratedFile:
        """Write content to a file, verifying path safety."""
        if not is_safe_generated_path(relative_path):
            raise ValueError(f"Unsafe path detected: {relative_path}")
            
        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return GeneratedFile(
            path=relative_path,
            purpose=purpose,
            owner_agent=owner_agent
        )

    def _backend_requirements(self) -> str:
        return "fastapi==0.111.0\nuvicorn==0.30.1\npydantic==2.7.4\n"

    def _backend_main_py(self, project_name: str) -> str:
        return f'''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from pathlib import Path

app = FastAPI(title="{project_name} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE_PATH = Path("data/store.json")

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: str
    items: List[CartItem]
    total: float

def load_data():
    if not STORE_PATH.exists():
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_data = {{"products": [], "cart": [], "orders": []}}
        with open(STORE_PATH, "w") as f:
            json.dump(default_data, f)
        return default_data
    with open(STORE_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f)

# Initialize data if not exists
load_data()

@app.get("/health")
def health():
    return {{"status": "ok"}}

@app.get("/products", response_model=List[Product])
def get_products():
    data = load_data()
    return data.get("products", [])

@app.get("/products/{{product_id}}", response_model=Product)
def get_product(product_id: str):
    data = load_data()
    for p in data.get("products", []):
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/cart/items")
def add_to_cart(item: CartItem):
    data = load_data()
    cart = data.get("cart", [])
    
    # Simple check if product exists
    products = data.get("products", [])
    if not any(p["id"] == item.product_id for p in products):
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Update quantity if exists, else append
    for c_item in cart:
        if c_item["product_id"] == item.product_id:
            c_item["quantity"] += item.quantity
            save_data(data)
            return {{"status": "success", "cart": cart}}
            
    cart.append(item.model_dump())
    save_data(data)
    return {{"status": "success", "cart": cart}}

@app.get("/cart", response_model=List[CartItem])
def get_cart():
    data = load_data()
    return data.get("cart", [])

@app.delete("/cart")
def clear_cart():
    data = load_data()
    data["cart"] = []
    save_data(data)
    return {{"status": "success"}}

@app.post("/checkout", response_model=Order)
def checkout():
    data = load_data()
    cart = data.get("cart", [])
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    products = {{p["id"]: p for p in data.get("products", [])}}
    total = sum(products[item["product_id"]]["price"] * item["quantity"] for item in cart)
    
    order_id = f"ORD-{{len(data.get('orders', [])) + 1:04d}}"
    order = {{"id": order_id, "items": cart, "total": total}}
    
    data.setdefault("orders", []).append(order)
    data["cart"] = [] # Clear cart
    save_data(data)
    
    return order

@app.get("/orders", response_model=List[Order])
def get_orders():
    data = load_data()
    return data.get("orders", [])
'''

    def _store_json(self) -> str:
        data = {
            "products": [
                {"id": "P001", "name": "Laptop", "description": "High performance laptop", "price": 1200.0},
                {"id": "P002", "name": "Mouse", "description": "Wireless mouse", "price": 25.0},
                {"id": "P003", "name": "Keyboard", "description": "Mechanical keyboard", "price": 75.0}
            ],
            "cart": [],
            "orders": []
        }
        return json.dumps(data, indent=2)

    def _frontend_index_html(self, project_name: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>{project_name}</h1>
        <nav>
            <button onclick="showProducts()">Products</button>
            <button onclick="showCart()">Cart (<span id="cart-count">0</span>)</button>
            <button onclick="showOrders()">Orders</button>
        </nav>
    </header>

    <main id="app-content">
        <!-- Content loaded dynamically -->
    </main>

    <script>
        const API_BASE = "http://127.0.0.1:9000";

        async function fetchAPI(endpoint, method = "GET", body = null) {{
            const options = {{ method, headers: {{ "Content-Type": "application/json" }} }};
            if (body) options.body = JSON.stringify(body);
            const res = await fetch(`${{API_BASE}}${{endpoint}}`, options);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }}

        async function showProducts() {{
            const content = document.getElementById("app-content");
            content.innerHTML = "<h2>Products</h2><div id='product-list' class='grid'>Loading...</div>";
            try {{
                const products = await fetchAPI("/products");
                const list = document.getElementById("product-list");
                list.innerHTML = products.map(p => `
                    <div class="card">
                        <h3>${{p.name}}</h3>
                        <p>${{p.description}}</p>
                        <p><strong>$${{p.price}}</strong></p>
                        <button onclick="addToCart('${{p.id}}')">Add to Cart</button>
                    </div>
                `).join('');
            }} catch (e) {{
                document.getElementById("product-list").innerHTML = `<p class="error">${{e.message}}</p>`;
            }}
        }}

        async function addToCart(productId) {{
            try {{
                await fetchAPI("/cart/items", "POST", {{ product_id: productId, quantity: 1 }});
                alert("Added to cart!");
                updateCartCount();
            }} catch (e) {{
                alert("Error adding to cart: " + e.message);
            }}
        }}

        async function updateCartCount() {{
            try {{
                const cart = await fetchAPI("/cart");
                const count = cart.reduce((sum, item) => sum + item.quantity, 0);
                document.getElementById("cart-count").innerText = count;
            }} catch (e) {{
                console.error("Failed to update cart count");
            }}
        }}

        async function showCart() {{
            const content = document.getElementById("app-content");
            content.innerHTML = "<h2>Cart</h2><div id='cart-content'>Loading...</div>";
            try {{
                const cart = await fetchAPI("/cart");
                const products = await fetchAPI("/products");
                const productMap = products.reduce((acc, p) => ({{...acc, [p.id]: p}}), {{}});
                
                const cartHtml = cart.map(item => `
                    <div class="cart-item">
                        <span>${{productMap[item.product_id]?.name || item.product_id}}</span>
                        <span>Qty: ${{item.quantity}}</span>
                    </div>
                `).join('');
                
                document.getElementById("cart-content").innerHTML = `
                    <div class="cart-list">${{cartHtml || '<p>Cart is empty</p>'}}</div>
                    ${{cart.length > 0 ? '<button onclick="checkout()">Checkout</button>' : ''}}
                `;
            }} catch (e) {{
                document.getElementById("cart-content").innerHTML = `<p class="error">${{e.message}}</p>`;
            }}
        }}

        async function checkout() {{
            try {{
                await fetchAPI("/checkout", "POST");
                alert("Checkout successful!");
                updateCartCount();
                showOrders();
            }} catch (e) {{
                alert("Checkout failed: " + e.message);
            }}
        }}

        async function showOrders() {{
            const content = document.getElementById("app-content");
            content.innerHTML = "<h2>Orders</h2><div id='order-list'>Loading...</div>";
            try {{
                const orders = await fetchAPI("/orders");
                document.getElementById("order-list").innerHTML = orders.map(o => `
                    <div class="card">
                        <h3>Order: ${{o.id}}</h3>
                        <p>Total: $${{o.total}}</p>
                        <p>Items: ${{o.items.reduce((sum, i) => sum + i.quantity, 0)}}</p>
                    </div>
                `).join('');
            }} catch (e) {{
                document.getElementById("order-list").innerHTML = `<p class="error">${{e.message}}</p>`;
            }}
        }}

        // Initial load
        showProducts();
        updateCartCount();
    </script>
</body>
</html>
'''

    def _frontend_styles_css(self) -> str:
        return '''body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
}
header {
    background-color: #333;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
nav button {
    background: none;
    border: none;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    margin-left: 1rem;
}
nav button:hover {
    text-decoration: underline;
}
main {
    padding: 2rem;
    max-width: 800px;
    margin: auto;
}
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}
.card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}
button:hover {
    background-color: #0056b3;
}
.cart-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    border-bottom: 1px solid #ccc;
}
.error {
    color: red;
}
'''

    def _docker_compose(self) -> str:
        return '''version: '3.8'
services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    volumes:
      - ./backend/data:/app/data
'''

    def _gitignore(self) -> str:
        return '''__pycache__/
*.pyc
venv/
.env
data/store.json
'''

    def _readme(self, project_name: str, functional_requirements: list) -> str:
        return f'''# {project_name}

Runnable E-commerce prototype generated by AutoForge Coder Agent.

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 9000
```
API Docs: http://127.0.0.1:9000/docs

### Frontend
Just open `frontend/index.html` in your browser.
Ensure backend is running.

### Docker
```bash
docker-compose up --build
```
'''

    def _responsibilities(self) -> list:
        return [
            ResponsibilitySummary(
                agent_name="Development Agent",
                responsibility="Generates application logic, backend API, minimal frontend, and workflows",
                outputs=["backend/main.py", "frontend/index.html", "frontend/styles.css"]
            ),
            ResponsibilitySummary(
                agent_name="Database Agent",
                responsibility="Defines data layer, models, and JSON data store for MVP",
                outputs=["backend/data/store.json"]
            ),
            ResponsibilitySummary(
                agent_name="DevOps Agent",
                responsibility="Generates deployment files and run instructions",
                outputs=["docker-compose.yml", "README.md", ".gitignore"]
            )
        ]

    def _traceability_links(self, functional_requirements: list) -> list:
        links = []
        for req in functional_requirements:
            req_id = req.get("id", "UNKNOWN")
            title = req.get("title", "Unknown Requirement")
            
            # Simple heuristic tracing based on title
            endpoints = []
            files = ["backend/main.py"]
            title_lower = title.lower()
            
            if "product" in title_lower or "catalog" in title_lower:
                endpoints.extend(["GET /products", "GET /products/{product_id}"])
                files.extend(["frontend/index.html"])
            elif "cart" in title_lower:
                endpoints.extend(["POST /cart/items", "GET /cart", "DELETE /cart"])
                files.extend(["frontend/index.html"])
            elif "checkout" in title_lower or "order" in title_lower:
                endpoints.extend(["POST /checkout", "GET /orders"])
                files.extend(["frontend/index.html"])
                
            links.append(TraceabilityLink(
                requirement_id=req_id,
                requirement_title=title,
                generated_files=files,
                api_endpoints=endpoints
            ))
            
        return links

    def generate_code(self, run_id: str, srs_version: str = "v1", code_version: str = "v1") -> dict:
        """Generate the application code from SRS."""
        srs_data = self._load_srs(run_id, srs_version)
        
        project_name = "Generated App"
        functional_reqs = []
        
        if srs_data:
            metadata = srs_data.get("metadata", {})
            project_name = metadata.get("project_name", "E-Commerce App")
            sections = srs_data.get("sections", {})
            functional_reqs = sections.get("functional_requirements", [])
            
        base_dir = self.output_dir / "runs" / run_id / "code" / code_version / "generated_app"
        
        generated_files = []
        
        # 1. Backend Code
        f = self._write_file(base_dir, "backend/requirements.txt", self._backend_requirements(), "Dependencies", "Development Agent")
        generated_files.append(f)
        
        f = self._write_file(base_dir, "backend/main.py", self._backend_main_py(project_name), "API endpoints and models", "Development Agent")
        generated_files.append(f)
        
        f = self._write_file(base_dir, "backend/data/store.json", self._store_json(), "Initial JSON data store", "Database Agent")
        generated_files.append(f)
        
        # 2. Frontend Code
        f = self._write_file(base_dir, "frontend/index.html", self._frontend_index_html(project_name), "Main UI", "Development Agent")
        generated_files.append(f)
        
        f = self._write_file(base_dir, "frontend/styles.css", self._frontend_styles_css(), "UI Styling", "Development Agent")
        generated_files.append(f)
        
        # 3. DevOps Code
        f = self._write_file(base_dir, "docker-compose.yml", self._docker_compose(), "Container orchestration", "DevOps Agent")
        generated_files.append(f)
        
        f = self._write_file(base_dir, ".gitignore", self._gitignore(), "Git ignore paths", "DevOps Agent")
        generated_files.append(f)
        
        f = self._write_file(base_dir, "README.md", self._readme(project_name, functional_reqs), "Project documentation", "DevOps Agent")
        generated_files.append(f)
        
        # Generate Manifest
        manifest = CodeManifest(
            run_id=run_id,
            code_version=code_version,
            source_srs_version=srs_version,
            output_dir=str(base_dir),
            generated_files=generated_files,
            responsibilities=self._responsibilities(),
            traceability_links=self._traceability_links(functional_reqs),
            run_instructions=[
                "cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 9000",
                "Open frontend/index.html in browser"
            ]
        )
        
        manifest_path = self.output_dir / "runs" / run_id / "code" / code_version / f"CodeManifest_{code_version}.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))
            
        return {
            "status": "success",
            "run_id": run_id,
            "code_version": code_version,
            "manifest_path": str(manifest_path),
            "output_dir": str(base_dir)
        }

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from pathlib import Path

app = FastAPI(title="E-Commerce App API", version="1.0.0")

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
        default_data = {"products": [], "cart": [], "orders": []}
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
    return {"status": "ok"}

@app.get("/products", response_model=List[Product])
def get_products():
    data = load_data()
    return data.get("products", [])

@app.get("/products/{product_id}", response_model=Product)
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
            return {"status": "success", "cart": cart}
            
    cart.append(item.model_dump())
    save_data(data)
    return {"status": "success", "cart": cart}

@app.get("/cart", response_model=List[CartItem])
def get_cart():
    data = load_data()
    return data.get("cart", [])

@app.delete("/cart")
def clear_cart():
    data = load_data()
    data["cart"] = []
    save_data(data)
    return {"status": "success"}

@app.post("/checkout", response_model=Order)
def checkout():
    data = load_data()
    cart = data.get("cart", [])
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    products = {p["id"]: p for p in data.get("products", [])}
    total = sum(products[item["product_id"]]["price"] * item["quantity"] for item in cart)
    
    order_id = f"ORD-{len(data.get('orders', [])) + 1:04d}"
    order = {"id": order_id, "items": cart, "total": total}
    
    data.setdefault("orders", []).append(order)
    data["cart"] = [] # Clear cart
    save_data(data)
    
    return order

@app.get("/orders", response_model=List[Order])
def get_orders():
    data = load_data()
    return data.get("orders", [])

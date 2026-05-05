from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uvicorn import run as run_uvicorn
import uvicorn
import json
from backend.data.store import Store

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    customer_name: str
    total_price: float
    order_status: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/products")
async def read_products():
    products = Store().get_all_products()
    return {"products": [Product(**product).dict() for product in products]}

@app.get("/products/{product_id}")
async def read_product(product_id: int):
    product = Store().get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": Product(**product).dict()}

@app.post("/cart/items")
async def add_to_cart(cart_item: CartItem):
    # TO DO: Implement cart logic
    pass

@app.get("/cart")
async def read_cart():
    # TO DO: Implement cart logic
    pass

@app.delete("/cart")
async def delete_cart():
    # TO DO: Implement cart logic
    pass

@app.post("/checkout")
async def checkout(order: Order):
    # TO DO: Implement checkout logic
    pass

@app.get("/orders")
async def read_orders():
    orders = Store().get_all_orders()
    return {"orders": [Order(**order).dict() for order in orders]}

if __name__ == "__main__":
    run_uvicorn(app, host="0.0.0.0", port=9000)
import hashlib
import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

SECRET_KEY = "super-secret-key"
API_KEY = "12345-test-api-key"
DB_PASSWORD = "admin123"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/products")
def get_products():
    return [
        {"id": 1, "name": "Laptop", "price": 1500},
        {"id": 2, "name": "Phone", "price": 900}
    ]


@app.get("/search")
def search_product(keyword: str):
    query = "SELECT * FROM products WHERE name = '" + keyword + "'"
    return {"query": query}


@app.get("/hash")
def weak_hash(value: str):
    return hashlib.md5(value.encode()).hexdigest()


@app.get("/danger")
def dangerous_code(user_input: str):
    return eval(user_input)


@app.get("/run")
def run_command(command: str):
    subprocess.run(command, shell=True)
    return {"status": "executed"}

cart = []


def add_to_cart(product_id: int, quantity: int):
    """
    Add a product to the shopping cart.
    """

    item = {
        "product_id": product_id,
        "quantity": quantity
    }

    cart.append(item)

    return {
        "message": "Product added to cart",
        "cart": cart
    }


def view_cart():
    """
    View current cart items.
    """

    return {
        "cart": cart
    }


def checkout(customer_id: int):
    """
    Perform a mock checkout operation.
    """

    if not cart:
        return {
            "status": "failed",
            "message": "Cannot checkout with an empty cart"
        }

    return {
        "status": "success",
        "message": "Checkout completed",
        "customer_id": customer_id,
        "cart": cart
    }


def create_order(customer_id: int):
    """
    Create a mock order after checkout.
    """

    return {
        "order_id": 1,
        "customer_id": customer_id,
        "status": "created",
        "items": cart
    }

def get_product(product_id):
    if product_id is None:
        return {"error": "missing product id"}
    if product_id <= 0:
        return {"error": "invalid product id"}
    return {"id": product_id, "name": "Demo Product", "price": 100, "stock": 10}


def validate_quantity(quantity):
    if quantity <= 0:
        return {"error": "invalid quantity, quantity must be positive and greater than 0"}
    return {"quantity": quantity}


def checkout(cart, customer=None, payment=None):
    if not cart:
        return {"error": "cannot checkout with an empty cart"}
    if customer is None:
        return {"error": "missing customer required"}
    if payment is None:
        return {"error": "missing payment required"}

    return {"order_id": 1, "status": "created", "payment": "mock"}


def validate_price(price):
    if price <= 0:
        return {"error": "invalid price"}
    return {"price": price}


def check_stock(product_id, quantity):
    available_quantity = 10
    if quantity > available_quantity:
        return {"error": "insufficient stock / out of stock"}
    return {"status": "in stock"}

def place_order(customer_id):
    return create_order(customer_id)
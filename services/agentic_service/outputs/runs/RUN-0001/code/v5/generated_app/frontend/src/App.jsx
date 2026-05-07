import React, { useState, useEffect } from 'react';
import api from './api';

const App = () => {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);

  useEffect(() => {
    fetchProducts();
    fetchCart();
    fetchOrderHistory();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart');
      setCart(response.data.items);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  const fetchOrderHistory = async () => {
    try {
      const response = await api.get('/orders');
      setOrderHistory(response.data);
    } catch (error) {
      console.error('Error fetching order history:', error);
    }
  };

  const addToCart = async (productId, quantity) => {
    try {
      await api.post('/cart/items', { productId, quantity });
      fetchCart();
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await api.delete(`/cart/items/${itemId}`);
      fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  const updateCartItem = async (itemId, quantity) => {
    try {
      await api.put(`/cart/items/${itemId}`, { quantity });
      fetchCart();
    } catch (error) {
      console.error('Error updating cart item:', error);
    }
  };

  const checkout = async () => {
    try {
      await api.post('/checkout');
      fetchCart();
      fetchOrderHistory();
    } catch (error) {
      console.error('Error checking out:', error);
    }
  };

  return (
    <div className="app">
      <h1>AutoForge Shop</h1>
      <div className="product-catalog">
        {products.map((product) => (
          <div key={product.id} className="product-item">
            <img src={product.image} alt={product.name} />
            <h2>{product.name}</h2>
            <p>${product.price}</p>
            <button onClick={() => addToCart(product.id, 1)}>Add to Cart</button>
          </div>
        ))}
      </div>
      <div className="cart">
        <h2>Shopping Cart</h2>
        {cart.map((item) => (
          <div key={item.productId} className="cart-item">
            <img src={item.product.image} alt={item.product.name} />
            <h3>{item.product.name}</h3>
            <p>${item.product.price * item.quantity}</p>
            <input
              type="number"
              value={item.quantity}
              onChange={(e) => updateCartItem(item.productId, parseInt(e.target.value))}
            />
            <button onClick={() => removeFromCart(item.id)}>Remove</button>
          </div>
        ))}
        <button onClick={checkout}>Checkout</button>
      </div>
      <div className="order-history">
        <h2>Order History</h2>
        {orderHistory.map((order) => (
          <div key={order.id} className="order-item">
            <p>Order ID: {order.id}</p>
            <p>Status: {order.status}</p>
            <p>Total: ${order.total}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
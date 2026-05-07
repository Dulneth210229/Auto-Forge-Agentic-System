import React, { useState, useEffect } from 'react'
import { fetchProducts, fetchProduct, fetchCart, addToCart, updateCart, removeFromCart, checkoutCart, fetchOrders } from './api'

const App = () => {
  const [products, setProducts] = useState([])
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [cart, setCart] = useState([])
  const [orders, setOrders] = useState([])
  const [view, setView] = useState('catalog')
  const [searchTerm, setSearchTerm] = useState('')
  const [cartUpdated, setCartUpdated] = useState(false)

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await fetchProducts()
        setProducts(data)
      } catch (error) {
        console.error('Failed to fetch products:', error)
      }
    }

    const loadCart = async () => {
      try {
        const data = await fetchCart()
        setCart(data.items || [])
      } catch (error) {
        console.error('Failed to fetch cart:', error)
      }
    }

    const loadOrders = async () => {
      try {
        const data = await fetchOrders()
        setOrders(data)
      } catch (error) {
        console.error('Failed to fetch orders:', error)
      }
    }

    loadProducts()
    loadCart()
    loadOrders()
  }, [cartUpdated])

  const handleAddToCart = async (productId, quantity = 1) => {
    try {
      const response = await addToCart(productId, quantity)
      setCart(response.items || [])
      setCartUpdated(!cartUpdated)
    } catch (error) {
      console.error('Failed to add to cart:', error)
    }
  }

  const handleUpdateCart = async (itemId, quantity) => {
    try {
      const response = await updateCart(itemId, quantity)
      setCart(response.items || [])
      setCartUpdated(!cartUpdated)
    } catch (error) {
      console.error('Failed to update cart:', error)
    }
  }

  const handleRemoveFromCart = async (itemId) => {
    try {
      await removeFromCart(itemId)
      setCart(cart.filter(item => item._id !== itemId))
      setCartUpdated(!cartUpdated)
    } catch (error) {
      console.error('Failed to remove from cart:', error)
    }
  }

  const handleCheckout = async () => {
    try {
      const response = await checkoutCart()
      alert('Order placed successfully!')
      setCart([])
      setCartUpdated(!cartUpdated)
      setView('orders')
    } catch (error) {
      console.error('Checkout failed:', error)
      alert('Checkout failed. Please try again.')
    }
  }

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const totalCartPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)

  return (
    <div className="app">
      <header className="app-header">
        <h1>AutoForge Shop</h1>
        <nav>
          <button onClick={() => setView('catalog')}>Products</button>
          <button onClick={() => setView('cart')}>Cart ({cart.length})</button>
          <button onClick={() => setView('orders')}>Orders</button>
        </nav>
      </header>

      <main className="app-main">
        {view === 'catalog' && (
          <div className="catalog">
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="product-grid">
              {filteredProducts.map(product => (
                <div key={product._id} className="product-card">
                  <img src={product.image} alt={product.name} />
                  <h3>{product.name}</h3>
                  <p className="price">${product.price}</p>
                  <p>{product.description}</p>
                  <button onClick={() => setSelectedProduct(product)}>View Details</button>
                  <button onClick={() => handleAddToCart(product._id)}>Add to Cart</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'cart' && (
          <div className="cart">
            <h2>Shopping Cart</h2>
            {cart.length === 0 ? (
              <p>Your cart is empty</p>
            ) : (
              <>
                <div className="cart-items">
                  {cart.map(item => (
                    <div key={item._id} className="cart-item">
                      <span>{item.name} x {item.quantity}</span>
                      <span>${item.price * item.quantity}</span>
                      <button onClick={() => handleRemoveFromCart(item._id)}>Remove</button>
                    </div>
                  ))}
                </div>
                <div className="cart-summary">
                  <p>Total: ${totalCartPrice.toFixed(2)}</p>
                  <button onClick={handleCheckout}>Checkout</button>
                </div>
              </>
            )}
          </div>
        )}

        {view === 'orders' && (
          <div className="orders">
            <h2>Order History</h2>
            {orders.length === 0 ? (
              <p>No orders found</p>
            ) : (
              <div className="order-list">
                {orders.map(order => (
                  <div key={order._id} className="order-item">
                    <p>Order #{order._id}</p>
                    <p>Status: {order.status}</p>
                    <p>Total: ${order.total}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {selectedProduct && (
          <div className="modal">
            <div className="modal-content">
              <span className="close" onClick={() => setSelectedProduct(null)}>&times;</span>
              <img src={selectedProduct.image} alt={selectedProduct.name} />
              <h2>{selectedProduct.name}</h2>
              <p className="price">${selectedProduct.price}</p>
              <p>{selectedProduct.description}</p>
              <p>Category: {selectedProduct.category}</p>
              <button onClick={() => handleAddToCart(selectedProduct._id)}>Add to Cart</button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
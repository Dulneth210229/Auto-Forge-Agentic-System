const API_BASE_URL = 'http://127.0.0.1:9000'

export const fetchProducts = async () => {
  const response = await fetch(`${API_BASE_URL}/products`)
  if (!response.ok) {
    throw new Error('Failed to fetch products')
  }
  return response.json()
}

export const fetchProduct = async (productId) => {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch product')
  }
  return response.json()
}

export const fetchCart = async () => {
  const response = await fetch(`${API_BASE_URL}/cart`)
  if (!response.ok) {
    throw new Error('Failed to fetch cart')
  }
  return response.json()
}

export const addToCart = async (productId, quantity = 1) => {
  const response = await fetch(`${API_BASE_URL}/cart/items`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_id: productId, quantity }),
  })
  if (!response.ok) {
    throw new Error('Failed to add to cart')
  }
  return response.json()
}

export const updateCart = async (itemId, quantity) => {
  const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ quantity }),
  })
  if (!response.ok) {
    throw new Error('Failed to update cart')
  }
  return response.json()
}

export const removeFromCart = async (itemId) => {
  const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to remove from cart')
  }
  return response.json()
}

export const checkoutCart = async () => {
  const response = await fetch(`${API_BASE_URL}/checkout`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Checkout failed')
  }
  return response.json()
}

export const fetchOrders = async () => {
  const response = await fetch(`${API_BASE_URL}/orders`)
  if (!response.ok) {
    throw new Error('Failed to fetch orders')
  }
  return response.json()
}
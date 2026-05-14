const {
  CartItem,
  Product
} = require('../models/index');

const calculateCartTotal = async (cartItems) => {
  let total = 0;
  for (const item of cartItems) {
    total += item.quantity * item.unit_price;
  }
  return total;
};

const validateProductAvailability = async (product_id, quantity) => {
  const product = await Product.findById(product_id);
  if (!product || product.stock_quantity < quantity) {
    throw new Error('Insufficient stock');
  }
  return true;
};

module.exports = {
  calculateCartTotal,
  validateProductAvailability
};
const mongoose = require('mongoose');

// User model
const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password_hash: { type: String, required: true },
  role: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

// Category model
const categorySchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: { type: String }
});

const Category = mongoose.model('Category', categorySchema);

// Product model
const productSchema = new mongoose.Schema({
  category_id: { type: mongoose.Types.ObjectId, ref: 'Category', required: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  price: { type: Number, required: true },
  stock_quantity: { type: Number, required: true },
  image_url: { type: String },
  is_active: { type: Boolean, default: true }
});

const Product = mongoose.model('Product', productSchema);

// Cart model
const cartSchema = new mongoose.Schema({
  user_id: { type: mongoose.Types.ObjectId, ref: 'User', required: true },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

const Cart = mongoose.model('Cart', cartSchema);

// CartItem model
const cartItemSchema = new mongoose.Schema({
  cart_id: { type: mongoose.Types.ObjectId, ref: 'Cart', required: true },
  product_id: { type: mongoose.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

const CartItem = mongoose.model('CartItem', cartItemSchema);

// Order model
const orderSchema = new mongoose.Schema({
  user_id: { type: mongoose.Types.ObjectId, ref: 'User', required: true },
  status: { type: String, default: 'pending' },
  total_amount: { type: Number, required: true },
  created_at: { type: Date, default: Date.now }
});

const Order = mongoose.model('Order', orderSchema);

// OrderItem model
const orderItemSchema = new mongoose.Schema({
  order_id: { type: mongoose.Types.ObjectId, ref: 'Order', required: true },
  product_id: { type: mongoose.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

const OrderItem = mongoose.model('OrderItem', orderItemSchema);

// Payment model
const paymentSchema = new mongoose.Schema({
  order_id: { type: mongoose.Types.ObjectId, ref: 'Order', required: true },
  method: { type: String, required: true },
  status: { type: String, default: 'pending' },
  transaction_reference: { type: String }
});

const Payment = mongoose.model('Payment', paymentSchema);

// Address model
const addressSchema = new mongoose.Schema({
  user_id: { type: mongoose.Types.ObjectId, ref: 'User', required: true },
  line1: { type: String, required: true },
  city: { type: String, required: true },
  postal_code: { type: String, required: true },
  country: { type: String, required: true }
});

const Address = mongoose.model('Address', addressSchema);

module.exports = {
  User,
  Category,
  Product,
  Cart,
  CartItem,
  Order,
  OrderItem,
  Payment,
  Address
};
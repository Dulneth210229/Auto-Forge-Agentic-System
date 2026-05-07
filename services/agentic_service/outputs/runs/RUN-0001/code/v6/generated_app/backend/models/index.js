const mongoose = require('mongoose');

const { Schema } = mongoose;

// User Schema
const userSchema = new Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password_hash: { type: String, required: true },
  role: { type: String, required: true, default: 'customer' },
  created_at: { type: Date, default: Date.now }
});

// Category Schema
const categorySchema = new Schema({
  name: { type: String, required: true },
  description: { type: String }
});

// Product Schema
const productSchema = new Schema({
  category_id: { type: Schema.Types.ObjectId, ref: 'Category', required: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  price: { type: Number, required: true },
  stock_quantity: { type: Number, required: true },
  image_url: { type: String },
  is_active: { type: Boolean, required: true, default: true }
});

// Cart Schema
const cartSchema = new Schema({
  user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

// CartItem Schema
const cartItemSchema = new Schema({
  cart_id: { type: Schema.Types.ObjectId, ref: 'Cart', required: true },
  product_id: { type: Schema.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

// Order Schema
const orderSchema = new Schema({
  user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  status: { type: String, required: true, default: 'pending' },
  total_amount: { type: Number, required: true },
  created_at: { type: Date, default: Date.now }
});

// OrderItem Schema
const orderItemSchema = new Schema({
  order_id: { type: Schema.Types.ObjectId, ref: 'Order', required: true },
  product_id: { type: Schema.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

// Payment Schema
const paymentSchema = new Schema({
  order_id: { type: Schema.Types.ObjectId, ref: 'Order', required: true },
  method: { type: String, required: true },
  status: { type: String, required: true, default: 'pending' },
  transaction_reference: { type: String }
});

// Address Schema
const addressSchema = new Schema({
  user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  line1: { type: String, required: true },
  city: { type: String, required: true },
  postal_code: { type: String, required: true },
  country: { type: String, required: true }
});

module.exports = {
  User: mongoose.model('User', userSchema),
  Category: mongoose.model('Category', categorySchema),
  Product: mongoose.model('Product', productSchema),
  Cart: mongoose.model('Cart', cartSchema),
  CartItem: mongoose.model('CartItem', cartItemSchema),
  Order: mongoose.model('Order', orderSchema),
  OrderItem: mongoose.model('OrderItem', orderItemSchema),
  Payment: mongoose.model('Payment', paymentSchema),
  Address: mongoose.model('Address', addressSchema)
};
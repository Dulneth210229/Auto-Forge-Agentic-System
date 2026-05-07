const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  id: { type: String, required: true },
  name: { type: String, required: true },
  email: { type: String, required: true },
  password_hash: { type: String, required: true },
  role: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});

const CategorySchema = new mongoose.Schema({
  id: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String }
});

const ProductSchema = new mongoose.Schema({
  id: { type: String, required: true },
  category_id: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String },
  price: { type: Number, required: true },
  stock_quantity: { type: Number, required: true },
  image_url: { type: String },
  is_active: { type: Boolean, default: true }
});

const CartSchema = new mongoose.Schema({
  id: { type: String, required: true },
  user_id: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

const CartItemSchema = new mongoose.Schema({
  id: { type: String, required: true },
  cart_id: { type: String, required: true },
  product_id: { type: String, required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

const OrderSchema = new mongoose.Schema({
  id: { type: String, required: true },
  user_id: { type: String, required: true },
  status: { type: String, required: true },
  total_amount: { type: Number, required: true },
  created_at: { type: Date, default: Date.now }
});

const OrderItemSchema = new mongoose.Schema({
  id: { type: String, required: true },
  order_id: { type: String, required: true },
  product_id: { type: String, required: true },
  quantity: { type: Number, required: true },
  unit_price: { type: Number, required: true }
});

const PaymentSchema = new mongoose.Schema({
  id: { type: String, required: true },
  order_id: { type: String, required: true },
  method: { type: String, required: true },
  status: { type: String, required: true },
  transaction_reference: { type: String }
});

const AddressSchema = new mongoose.Schema({
  id: { type: String, required: true },
  user_id: { type: String, required: true },
  line1: { type: String, required: true },
  city: { type: String, required: true },
  postal_code: { type: String, required: true },
  country: { type: String, required: true }
});

module.exports = {
  User: mongoose.model('User', UserSchema),
  Category: mongoose.model('Category', CategorySchema),
  Product: mongoose.model('Product', ProductSchema),
  Cart: mongoose.model('Cart', CartSchema),
  CartItem: mongoose.model('CartItem', CartItemSchema),
  Order: mongoose.model('Order', OrderSchema),
  OrderItem: mongoose.model('OrderItem', OrderItemSchema),
  Payment: mongoose.model('Payment', PaymentSchema),
  Address: mongoose.model('Address', AddressSchema)
};
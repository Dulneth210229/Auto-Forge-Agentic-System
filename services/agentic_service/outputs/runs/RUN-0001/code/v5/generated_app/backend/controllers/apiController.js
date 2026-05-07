const { User, Product, Cart, CartItem, Order, OrderItem } = require('../models');
const bcrypt = require('bcrypt');

// Register user
exports.registerUser = async (req, res) => {
  const { name, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const newUser = new User({ name, email, password_hash: hashedPassword, role: 'customer' });
  await newUser.save();
  res.status(201).json(newUser);
};

// Login user
exports.loginUser = async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || !await bcrypt.compare(password, user.password_hash)) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  res.json(user);
};

// List products
exports.listProducts = async (req, res) => {
  const products = await Product.find();
  res.json(products);
};

// Get product details
exports.getProductDetails = async (req, res) => {
  const { product_id } = req.params;
  const product = await Product.findById(product_id);
  if (!product) {
    return res.status(404).json({ message: 'Product not found' });
  }
  res.json(product);
};

// Get cart
exports.getCart = async (req, res) => {
  const { user_id } = req.body;
  const cart = await Cart.findOne({ user_id }).populate('cart_items.product_id');
  if (!cart) {
    return res.status(404).json({ message: 'Cart not found' });
  }
  res.json(cart);
};

// Add item to cart
exports.addItemToCart = async (req, res) => {
  const { user_id, product_id, quantity } = req.body;
  let cart = await Cart.findOne({ user_id });
  if (!cart) {
    cart = new Cart({ user_id });
  }
  const existingItem = cart.cart_items.find(item => item.product_id.toString() === product_id);
  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.cart_items.push({ product_id, quantity, unit_price: await Product.findById(product_id).price });
  }
  await cart.save();
  res.json(cart);
};

// Update cart item
exports.updateCartItem = async (req, res) => {
  const { user_id, item_id, quantity } = req.body;
  const cart = await Cart.findOne({ user_id });
  if (!cart) {
    return res.status(404).json({ message: 'Cart not found' });
  }
  const itemIndex = cart.cart_items.findIndex(item => item._id.toString() === item_id);
  if (itemIndex !== -1) {
    cart.cart_items[itemIndex].quantity = quantity;
    await cart.save();
    res.json(cart);
  } else {
    return res.status(404).json({ message: 'Cart item not found' });
  }
};

// Remove item from cart
exports.removeItemFromCart = async (req, res) => {
  const { user_id, item_id } = req.body;
  const cart = await Cart.findOne({ user_id });
  if (!cart) {
    return res.status(404).json({ message: 'Cart not found' });
  }
  const itemIndex = cart.cart_items.findIndex(item => item._id.toString() === item_id);
  if (itemIndex !== -1) {
    cart.cart_items.splice(itemIndex, 1);
    await cart.save();
    res.json(cart);
  } else {
    return res.status(404).json({ message: 'Cart item not found' });
  }
};

// List order history
exports.listOrderHistory = async (req, res) => {
  const { user_id } = req.body;
  const orders = await Order.find({ user_id }).populate('order_items.product_id');
  res.json(orders);
};

// Place order
exports.placeOrder = async (req, res) => {
  const { user_id, cart_id } = req.body;
  const cart = await Cart.findById(cart_id).populate('cart_items.product_id');
  if (!cart) {
    return res.status(404).json({ message: 'Cart not found' });
  }
  const order = new Order({ user_id, total_amount: cart.cart_items.reduce((total, item) => total + (item.quantity * item.unit_price), 0) });
  for (const item of cart.cart_items) {
    const orderItem = new OrderItem({ order_id: order._id, product_id: item.product_id, quantity: item.quantity, unit_price: item.unit_price });
    await orderItem.save();
    order.order_items.push(orderItem);
  }
  await order.save();
  await Cart.findByIdAndDelete(cart_id);
  res.json(order);
};
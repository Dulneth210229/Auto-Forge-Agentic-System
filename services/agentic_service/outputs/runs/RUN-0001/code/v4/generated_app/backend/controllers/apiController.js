const { User, Category, Product, Cart, CartItem, Order, OrderItem } = require('../models');
const bcrypt = require('bcrypt');

async function registerUser(req, res) {
  const { name, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = new User({ id: uuidv4(), name, email, password_hash: hashedPassword, role: 'customer', created_at: new Date() });
  await user.save();
  res.status(201).json(user);
}

async function loginUser(req, res) {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (user && await bcrypt.compare(password, user.password_hash)) {
    res.json(user);
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
}

async function listProducts(req, res) {
  const products = await Product.find();
  res.json(products);
}

async function getProductDetails(req, res) {
  const { product_id } = req.params;
  const product = await Product.findById(product_id);
  if (product) {
    res.json(product);
  } else {
    res.status(404).json({ message: 'Product not found' });
  }
}

async function addItemToCart(req, res) {
  const { user_id, product_id, quantity } = req.body;
  let cart = await Cart.findOne({ user_id });
  if (!cart) {
    cart = new Cart({ id: uuidv4(), user_id, created_at: new Date() });
  }
  const item = new CartItem({ id: uuidv4(), cart_id: cart.id, product_id, quantity, unit_price: (await Product.findById(product_id)).price });
  await item.save();
  await cart.save();
  res.json(item);
}

async function updateCartItem(req, res) {
  const { item_id } = req.params;
  const { quantity } = req.body;
  const item = await CartItem.findById(item_id);
  if (item) {
    item.quantity = quantity;
    await item.save();
    res.json(item);
  } else {
    res.status(404).json({ message: 'Cart item not found' });
  }
}

async function removeCartItem(req, res) {
  const { item_id } = req.params;
  await CartItem.findByIdAndDelete(item_id);
  res.status(204).send();
}

async function getCart(req, res) {
  const user_id = req.user.id; // Assuming authentication middleware sets req.user
  const cart = await Cart.findOne({ user_id });
  if (cart) {
    const items = await CartItem.find({ cart_id: cart.id });
    res.json(items);
  } else {
    res.status(404).json({ message: 'Cart not found' });
  }
}

async function checkoutCart(req, res) {
  const user_id = req.user.id; // Assuming authentication middleware sets req.user
  const cart = await Cart.findOne({ user_id });
  if (cart) {
    let totalAmount = 0;
    for (const item of cart.items) {
      totalAmount += item.quantity * item.unit_price;
    }
    const order = new Order({ id: uuidv4(), user_id, status: 'pending', total_amount: totalAmount, created_at: new Date() });
    await order.save();
    for (const item of cart.items) {
      const orderItem = new OrderItem({ id: uuidv4(), order_id: order.id, product_id: item.product_id, quantity: item.quantity, unit_price: item.unit_price });
      await orderItem.save();
    }
    res.json(order);
  } else {
    res.status(404).json({ message: 'Cart not found' });
  }
}

async function placeOrder(req, res) {
  const { user_id } = req.body;
  const cart = await Cart.findOne({ user_id });
  if (cart) {
    let totalAmount = 0;
    for (const item of cart.items) {
      totalAmount += item.quantity * item.unit_price;
    }
    const order = new Order({ id: uuidv4(), user_id, status: 'placed', total_amount: totalAmount, created_at: new Date() });
    await order.save();
    for (const item of cart.items) {
      const orderItem = new OrderItem({ id: uuidv4(), order_id: order.id, product_id: item.product_id, quantity: item.quantity, unit_price: item.unit_price });
      await orderItem.save();
    }
    res.json(order);
  } else {
    res.status(404).json({ message: 'Cart not found' });
  }
}

async function listOrders(req, res) {
  const user_id = req.user.id; // Assuming authentication middleware sets req.user
  const orders = await Order.find({ user_id });
  res.json(orders);
}

module.exports = {
  registerUser,
  loginUser,
  listProducts,
  getProductDetails,
  addItemToCart,
  updateCartItem,
  removeCartItem,
  getCart,
  checkoutCart,
  placeOrder,
  listOrders
};
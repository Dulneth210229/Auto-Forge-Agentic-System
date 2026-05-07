const bcrypt = require('bcryptjs');
const {
  User,
  Category,
  Product,
  Cart,
  CartItem,
  Order,
  OrderItem,
  Payment,
  Address
} = require('../models/index');
const businessService = require('../services/businessService');

// Auth Controllers
const register = async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({
      name,
      email,
      password_hash: hashedPassword,
      role: 'customer'
    });
    await user.save();
    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    res.json({ message: 'Login successful', user: { id: user._id, name: user.name, email: user.email, role: user.role } });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Product Controllers
const getProducts = async (req, res) => {
  try {
    const { category, search, minPrice, maxPrice } = req.query;
    let filter = { is_active: true };
    if (category) filter.category_id = category;
    if (search) filter.name = { $regex: search, $options: 'i' };
    if (minPrice || maxPrice) {
      filter.price = {};
      if (minPrice) filter.price.$gte = parseFloat(minPrice);
      if (maxPrice) filter.price.$lte = parseFloat(maxPrice);
    }
    const products = await Product.find(filter).populate('category_id');
    res.json(products);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const getProductById = async (req, res) => {
  try {
    const product = await Product.findById(req.params.product_id).populate('category_id');
    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }
    res.json(product);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Cart Controllers
const getCart = async (req, res) => {
  try {
    const cart = await Cart.findOne({ user_id: req.user.id }).populate({
      path: 'items',
      populate: { path: 'product_id' }
    });
    if (!cart) {
      return res.json({ items: [] });
    }
    res.json(cart);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const addToCart = async (req, res) => {
  try {
    const { product_id, quantity } = req.body;
    const product = await Product.findById(product_id);
    if (!product || product.stock_quantity < quantity) {
      return res.status(400).json({ message: 'Insufficient stock' });
    }
    let cart = await Cart.findOne({ user_id: req.user.id });
    if (!cart) {
      cart = new Cart({ user_id: req.user.id });
      await cart.save();
    }
    const existingItem = await CartItem.findOne({ cart_id: cart._id, product_id });
    if (existingItem) {
      existingItem.quantity += quantity;
      await existingItem.save();
    } else {
      await CartItem.create({
        cart_id: cart._id,
        product_id,
        quantity,
        unit_price: product.price
      });
    }
    res.json({ message: 'Item added to cart' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const updateCartItem = async (req, res) => {
  try {
    const { quantity } = req.body;
    const item = await CartItem.findById(req.params.item_id);
    if (!item) {
      return res.status(404).json({ message: 'Item not found' });
    }
    const product = await Product.findById(item.product_id);
    if (product.stock_quantity < quantity) {
      return res.status(400).json({ message: 'Insufficient stock' });
    }
    item.quantity = quantity;
    await item.save();
    res.json({ message: 'Cart item updated' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const removeFromCart = async (req, res) => {
  try {
    await CartItem.findByIdAndDelete(req.params.item_id);
    res.json({ message: 'Item removed from cart' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Checkout Controller
const checkout = async (req, res) => {
  try {
    const cart = await Cart.findOne({ user_id: req.user.id }).populate({
      path: 'items',
      populate: { path: 'product_id' }
    });
    if (!cart || cart.items.length === 0) {
      return res.status(400).json({ message: 'Cart is empty' });
    }
    const total = await businessService.calculateCartTotal(cart.items);
    res.json({ total });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Order Controllers
const placeOrder = async (req, res) => {
  try {
    const cart = await Cart.findOne({ user_id: req.user.id }).populate({
      path: 'items',
      populate: { path: 'product_id' }
    });
    if (!cart || cart.items.length === 0) {
      return res.status(400).json({ message: 'Cart is empty' });
    }
    const total = await businessService.calculateCartTotal(cart.items);
    const order = new Order({
      user_id: req.user.id,
      total_amount: total
    });
    await order.save();
    for (const item of cart.items) {
      await OrderItem.create({
        order_id: order._id,
        product_id: item.product_id._id,
        quantity: item.quantity,
        unit_price: item.unit_price
      });
      await Product.findByIdAndUpdate(item.product_id._id, {
        $inc: { stock_quantity: -item.quantity }
      });
    }
    await Cart.findByIdAndDelete(cart._id);
    const payment = new Payment({
      order_id: order._id,
      method: 'mock',
      status: 'completed'
    });
    await payment.save();
    res.json({ message: 'Order placed successfully', order });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const getOrderHistory = async (req, res) => {
  try {
    const orders = await Order.find({ user_id: req.user.id }).populate('items');
    res.json(orders);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Admin Controller
const createProduct = async (req, res) => {
  try {
    const product = new Product(req.body);
    await product.save();
    res.status(201).json({ message: 'Product created successfully', product });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

module.exports = {
  register,
  login,
  getProducts,
  getProductById,
  getCart,
  addToCart,
  updateCartItem,
  removeFromCart,
  checkout,
  placeOrder,
  getOrderHistory,
  createProduct
};
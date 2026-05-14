const express = require('express');
const router = express.Router();
const apiController = require('../controllers/apiController');

// Auth Routes
router.post('/auth/register', apiController.register);
router.post('/auth/login', apiController.login);

// Product Routes
router.get('/products', apiController.getProducts);
router.get('/products/:product_id', apiController.getProductById);

// Cart Routes
router.get('/cart', apiController.getCart);
router.post('/cart/items', apiController.addToCart);
router.put('/cart/items/:item_id', apiController.updateCartItem);
router.delete('/cart/items/:item_id', apiController.removeFromCart);

// Checkout Route
router.post('/checkout', apiController.checkout);

// Order Routes
router.post('/orders', apiController.placeOrder);
router.get('/orders', apiController.getOrderHistory);

// Admin Routes
router.post('/admin/products', apiController.createProduct);

module.exports = router;
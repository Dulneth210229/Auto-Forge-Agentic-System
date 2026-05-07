const express = require('express');
const apiController = require('../controllers/apiController');

const router = express.Router();

// User routes
router.post('/auth/register', apiController.registerUser);
router.post('/auth/login', apiController.loginUser);

// Product routes
router.get('/products', apiController.listProducts);
router.get('/products/:product_id', apiController.getProductDetails);

// Cart routes
router.get('/cart', apiController.getCart);
router.post('/cart/items', apiController.addItemToCart);
router.put('/cart/items/:item_id', apiController.updateCartItem);
router.delete('/cart/items/:item_id', apiController.removeItemFromCart);

// Order routes
router.get('/orders', apiController.listOrderHistory);
router.post('/orders', apiController.placeOrder);

module.exports = router;
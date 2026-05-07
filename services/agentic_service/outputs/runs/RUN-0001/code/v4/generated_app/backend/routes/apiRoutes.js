const express = require('express');
const apiController = require('../controllers/apiController');

const router = express.Router();

router.post('/auth/register', apiController.registerUser);
router.post('/auth/login', apiController.loginUser);

router.get('/products', apiController.listProducts);
router.get('/products/:product_id', apiController.getProductDetails);

router.post('/cart/items', apiController.addItemToCart);
router.put('/cart/items/:item_id', apiController.updateCartItem);
router.delete('/cart/items/:item_id', apiController.removeCartItem);
router.get('/cart', apiController.getCart);

router.post('/checkout', apiController.checkoutCart);
router.post('/orders', apiController.placeOrder);
router.get('/orders', apiController.listOrders);

module.exports = router;
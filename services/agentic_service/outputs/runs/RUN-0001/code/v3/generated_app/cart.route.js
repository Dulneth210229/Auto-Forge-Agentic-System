const express = require('express');
const router = express.Router();
const CartController = require('../controllers/CartController');

router.get('/carts/:id', CartController.getCart);
router.put('/carts/:id', CartController.updateCart);

module.exports = router;
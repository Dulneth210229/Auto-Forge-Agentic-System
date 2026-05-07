const express = require('express');
const router = express.Router();
const ProductController = require('../controllers/ProductController');

router.get('/products/:id', ProductController.getProduct);
router.put('/products/:id', ProductController.updateProduct);

module.exports = router;
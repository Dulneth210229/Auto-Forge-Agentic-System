const express = require('express');
const router = express.Router();
const OrderController = require('../controllers/OrderController');

router.get('/orders/:id', OrderController.getOrder);
router.put('/orders/:id', OrderController.updateOrder);

module.exports = router;
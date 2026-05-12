const express = require('express');
const router = express.Router();
const ReviewController = require('../controllers/ReviewController');

router.get('/products/:id/reviews', ReviewController.getReviews);
router.post('/products/:id/reviews', ReviewController.createReview);

module.exports = router;
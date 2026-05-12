const express = require('express');
const router = express.Router();
const UserController = require('../controllers/UserController');

router.get('/users/:id', UserController.getUser);
router.put('/users/:id', UserController.updateUser);

module.exports = router;
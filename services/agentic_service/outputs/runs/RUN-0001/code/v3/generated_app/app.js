const express = require('express');
const app = express();
const userRoute = require('./routes/user.route');
const productRoute = require('./routes/product.route');
const cartRoute = require('./routes/cart.route');
const orderRoute = reviewRoute = require('./routes/order.route');

app.use(express.json());
app.use('/users', userRoute);
app.use('/products', productRoute);
app.use('/carts', cartRoute);
app.use('/orders', orderRoute);

module.exports = app;
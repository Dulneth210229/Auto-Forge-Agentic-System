const express = require('express');
const cors = require('cors');
const mongoose = require('./config/db');
const apiRoutes = require('./routes/apiRoutes');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api', apiRoutes);

mongoose.connect().then(() => {
  console.log('MongoDB connected');
}).catch(err => {
  console.error('MongoDB connection error:', err);
});

app.listen(9000, () => {
  console.log('Server is running on port 9000');
});
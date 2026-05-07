const mongoose = require('mongoose');

const addressSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  line1: { type: String, required: true },
  city: { type: String, required: true },
  postalCode: { type: String, required: true }
});

module.exports = mongoose.model('Address', addressSchema);
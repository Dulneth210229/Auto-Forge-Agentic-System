// Placeholder for reusable e-commerce business logic
module.exports = {
  validateProductAvailability: (product, quantity) => {
    return product.stock_quantity >= quantity;
  }
};
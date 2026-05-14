AutoForge Shop - MERN E-commerce Application

This is a modular monolith e-commerce application built with the MERN stack (MongoDB, Express.js, React, Node.js). The application follows a modular monolith architecture style for better organization and maintainability.

Prerequisites:
- Docker and Docker Compose installed
- Node.js and npm (for manual runs)
- Git

How to run with Docker Compose:
1. Clone the repository
2. Navigate to the project root directory
3. Run: docker-compose up --build
4. Access the frontend at http://localhost:5173
5. Access the backend API at http://localhost:9000

How to run backend manually:
1. Navigate to the backend directory
2. Install dependencies: npm install
3. Set environment variables (see below)
4. Run: npm run dev

How to run frontend manually:
1. Navigate to the frontend directory
2. Install dependencies: npm install
3. Set environment variables (see below)
4. Run: npm run dev

Environment Variable Setup:
Create a .env file in the backend directory with:
MONGO_URI=mongodb://localhost:27017/autoforge
PORT=9000

Useful URLs:
- Frontend: http://localhost:5173
- Backend API: http://localhost:9000
- MongoDB: mongodb://localhost:27017
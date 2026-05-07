# AutoForge Shop

## Overview
AutoForge Shop is a modular monolith e-commerce application built using the MERN stack. This project consists of three main components: backend, frontend, and MongoDB.

## Prerequisites
- Docker
- Docker Compose
- Node.js (v14 or later)
- npm or yarn

## Running with Docker Compose
To start the entire application using Docker Compose, run the following command in the root directory:

```sh
docker-compose up --build
```

This will build and start all services defined in `docker-compose.yml`.

## Running Backend Manually
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the server:
   ```sh
   npm start
   ```

The backend will run on `http://localhost:9000`.

## Running Frontend Manually
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm start
   ```

The frontend will run on `http://localhost:5173`.

## Environment Variable Setup
- For the backend, create a `.env` file in the `backend` directory with the following content:
  ```
  NODE_ENV=development
  MONGODB_URI=mongodb://mongodb:27017/autoforge
  ```

- For the frontend, set the `REACT_APP_API_URL` environment variable to point to your backend server.

## Useful URLs
- Backend API: [http://localhost:9000](http://localhost:9000)
- Frontend UI: [http://localhost:5173](http://localhost:5173)
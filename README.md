# bill-splitter

A small utility to split bills amongst friends

## Running the App

### Configuration

Before running the application, you need to set up environment variables:

1. Copy the backend example environment file

   ```bash
   cp .env.example .env
   ```

2. Copy the frontend example environment file

   ```bash
   cp frontend/.env.example frontend/.env
   ```

3. Edit the files and configure the variables as described in the example files.

### Spin up the services

To run the bill-splitter application, use Docker Compose:

```bash
docker compose up
```

This will start all necessary services for the application.

The backend service reads environment variables from the repo-root `.env`. The frontend service reads environment variables from `frontend/.env` and exposes them to the browser at container startup.

### Accessing the Frontend

Once the app is running, you can access the frontend at http://localhost:5173. This provides a user-friendly interface where you can split bills amongst friends.

### Accessing Backend Documentation

Once the app is running, you can access the interactive API documentation at http://localhost:8000/docs. This provides a Swagger UI interface where you can explore and test all available API endpoints.

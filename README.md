# bill-splitter

A small utility to split bills amongst friends

## Running the App

### Configuration

Before running the application, you need to set up environment variables:

1. Copy the example environment file

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and configure the variables

### Spin up the services

To run the bill-splitter application, use Docker Compose:

```bash
docker compose up
```

This will start all necessary services for the application.

### Accessing the Frontend

Once the app is running, you can access the frontend at http://localhost:5173. This provides a user-friendly interface where you can split bills amongst friends.

### Accessing Backend Documentation

Once the app is running, you can access the interactive API documentation at http://localhost:8000/docs. This provides a Swagger UI interface where you can explore and test all available API endpoints.

# =========================================
# Stage 1: Build the Python Application
# =========================================
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Configure uv to copy dependencies into the virtual environment and precompile bytecode
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency metadata first to leverage Docker's caching mechanism
COPY pyproject.toml uv.lock ./

# Install production dependencies without copying the application source
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# =========================================
# Stage 2: Prepare the FastAPI Runtime
# =========================================
FROM python:3.13-alpine AS runner

# Set the working directory inside the container
WORKDIR /app

# Create a non-root user to run the application
RUN addgroup -S billsplitter \
    && adduser -S -G billsplitter billsplitter

# Copy the virtual environment from the build stage
COPY --from=builder --chown=billsplitter:billsplitter /app/.venv /app/.venv

# Copy the application source code into the container
COPY --chown=billsplitter:billsplitter app ./app

# Use a non-root user for security best practices
USER billsplitter

# Run the FastAPI application
CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn app.main:app --host=0.0.0.0 --port=80 --workers=$(( $(nproc) * 2 + 1 ))"]

FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user to run the application.
RUN groupadd -g 999 billsplitter && useradd -m -r -u 999 -g billsplitter billsplitter
RUN mkdir /app && chown billsplitter:billsplitter /app

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
USER    billsplitter
RUN     uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]

# Stage 1: Use a lightweight Python image for building and installing dependencies
FROM python:3.11-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (sometimes needed for audio/science libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first (this speeds up rebuilding)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Create the final, minimal image
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy the rest of your app's code
COPY . .

# Security setup (User creation + Permissions in one go)
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser && \
    chown -R appuser:appgroup /app && \
    apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Expose the port FastAPI will run on
EXPOSE 8000

# Switch to the non-root user
USER appuser

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

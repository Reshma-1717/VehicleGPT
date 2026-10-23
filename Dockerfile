# ==========================================
# Stage 1: Build Frontend Assets
# ==========================================
FROM node:22-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Production Edge Container (ARM64 / AMD64)
# ==========================================
FROM python:3.11-slim

# System dependencies for SQLite WAL, edge networking & psutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code, scripts, sample data, and configuration
COPY backend/ ./backend/
COPY sample_data/ ./sample_data/
COPY scripts/ ./scripts/
COPY .env.example ./.env

# Copy compiled frontend from Stage 1 into backend static directory
COPY --from=frontend-builder /build/dist ./frontend/dist

# Create runtime directories for data & models
RUN mkdir -p /app/data /app/models

# Expose VehicleGPT Service Port
EXPOSE 8000

ENV APP_ENV=production \
    HARDWARE_PROFILE=constrained \
    HOST=0.0.0.0 \
    PORT=8000 \
    DATABASE_PATH=/app/data/vehiclegpt.db

# Run backend service
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

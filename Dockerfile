# Base Stage - Install dependencies
FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# ------------------------
# Production Stage (Default)
# ------------------------
FROM base AS prod
ENV FLASK_ENV=production
CMD ["gunicorn", "-b", "main:app"]

# ------------------------
# Development Stage (Optional)
# ------------------------
FROM base AS dev
ENV FLASK_ENV=development
CMD ["python", "main.py"]
# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Expose FastAPI default port
EXPOSE 8000

# Environment setup
ENV PYTHONUNBUFFERED=1

# Use Uvicorn as production server
CMD ["uvicorn", "rag_service:app", "--host", "0.0.0.0", "--port", "8000"]

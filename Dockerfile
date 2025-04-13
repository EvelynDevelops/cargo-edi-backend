# Use official slim Python image as base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (optional: needed for compiling packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Set environment variable to enable real-time logging
ENV PYTHONUNBUFFERED=1

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the app using Python module mode to avoid exec format issues
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

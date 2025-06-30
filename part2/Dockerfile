# Use a lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files and enable stdout buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (for httpx + SSL + DNS resolution)
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file from part1
COPY ../part1/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app source code
COPY ../part1 .

# Expose the port uvicorn will run on
EXPOSE 8000

# Run the FastAPI app with 2 workers (adjust based on CPU cores available)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY src/scraper/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/scraper/models.py .
COPY src/scraper/scraper_main.py .

# Create directory for database and logs (optional, for explicit volume mounting)
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# The application creates sqlite database and log files in current directory
# You may want to mount a volume to persist data
VOLUME ["/app/data"]

# Run the scraper
CMD ["python", "scraper_main.py"]

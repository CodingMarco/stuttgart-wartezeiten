# Stuttgart Waiting Times Scraper - Docker

This directory contains a dockerized version of the Stuttgart waiting times scraper.

## Building and Running

### Option 1: Using Docker directly

1. Build the Docker image:
   ```bash
   docker build -t stuttgart-scraper .
   ```

2. Run the container:
   ```bash
   docker run -d --name stuttgart-scraper -v scraper_data:/app stuttgart-scraper
   ```

### Option 2: Using Docker Compose (Recommended)

1. Build and start the service:
   ```bash
   docker-compose up -d
   ```

2. Stop the service:
   ```bash
   docker-compose down
   ```

## Data Persistence

The container creates two important files:
- `waiting_times.sqlite` - The SQLite database containing scraped data
- `scraper.log` - Application logs

Both files are stored in the `/app` directory inside the container. To persist this data between container restarts, the Docker configuration mounts a volume to this directory.

## Viewing Logs

To view the container logs:
```bash
# Using Docker
docker logs stuttgart-scraper

# Using Docker Compose
docker-compose logs scraper
```

To follow logs in real-time:
```bash
# Using Docker
docker logs -f stuttgart-scraper

# Using Docker Compose
docker-compose logs -f scraper
```

## Accessing the Database

To access the SQLite database from the host system:

1. Copy the database file from the container:
   ```bash
   docker cp stuttgart-scraper:/app/waiting_times.sqlite ./waiting_times.sqlite
   ```

2. Or, if using Docker Compose, you can find the volume location:
   ```bash
   docker volume inspect scraper_scraper_data
   ```

## Environment Variables

The container sets `PYTHONUNBUFFERED=1` to ensure logs are displayed in real-time.

## Resource Usage

The container is configured with memory limits:
- Maximum: 256MB
- Reserved: 128MB

These can be adjusted in the `docker-compose.yml` file if needed.

## Stopping the Scraper

```bash
# Using Docker
docker stop stuttgart-scraper

# Using Docker Compose
docker-compose stop
```

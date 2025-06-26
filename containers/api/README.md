# API Service Container Configuration

This directory will contain the Docker configuration for the REST API service.

## Structure (to be implemented)
- `Dockerfile` - Container build configuration
- `docker-compose.yml` - Service-specific compose configuration
- `.dockerignore` - Files to exclude from build context

## Notes
- The API will serve data collected by the scraper
- Will expose RESTful endpoints for waiting times data
- Should connect to the scraper's SQLite database (read-only)

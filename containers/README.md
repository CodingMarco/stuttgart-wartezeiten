# Containers

This directory contains all Docker-related configurations for the Stuttgart Wartezeiten project.

## Structure

```
containers/
├── docker-compose.yml          # Main orchestration file for all services
├── scraper/                    # Scraper service container config
│   ├── Dockerfile
│   ├── docker-compose.yml      # Individual service compose file
│   └── .dockerignore
├── api/                        # Future: REST API service (to be added)
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend/                   # Future: Frontend service (to be added)
    ├── Dockerfile
    └── docker-compose.yml
```

## Usage

### Run all services (main orchestration)
```bash
cd containers
docker-compose up -d
```

### Run individual services
```bash
# Run only the scraper
cd containers/scraper
docker-compose up -d

# Future: Run only the API
cd containers/api
docker-compose up -d
```

### Development
- The main `docker-compose.yml` sets up a shared network for all services
- Persistent data is stored in `./data/` directory
- Each service has its own subdirectory with individual Dockerfile and compose configuration

## Adding New Services

When adding a new service (e.g., REST API or frontend):

1. Create a new subdirectory under `containers/`
2. Add `Dockerfile` and `docker-compose.yml` for the service
3. Update the main `docker-compose.yml` to include the new service
4. Ensure proper networking and volume mounting for data sharing

## Notes

- All builds use the repository root as context for access to source code
- The scraper service persists data to `./data/scraper/`
- Services can communicate through the `stuttgart-network` bridge network

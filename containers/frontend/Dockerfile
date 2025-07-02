# Multi-stage build for Vue.js frontend
FROM node:22-alpine AS build-stage

WORKDIR /app

# Copy package files
COPY src/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/frontend/ ./

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine AS production-stage

# Copy built assets from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY containers/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

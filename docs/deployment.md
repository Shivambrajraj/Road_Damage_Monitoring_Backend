# Production Environment Deployment Guidelines

## Reverse Proxy Architecture
In production topologies, an Nginx reverse-proxy routes incoming traffic down to the internal Uvicorn ASGI loop listening on port 8000.

## Configuration Requirements
1. Ensure the production environment provides a robust, randomly generated sequence for `JWT_SECRET_KEY` inside `.env`.
2. Swap the file storage pathway (`UPLOAD_DIR`) to point toward a durable cloud bucket or network storage volume if running inside ephemeral cloud architectures.
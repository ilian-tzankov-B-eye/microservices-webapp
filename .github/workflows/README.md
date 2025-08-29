# WebApp Docker Build Workflow

This workflow automatically builds and pushes Docker images for the WebApp when changes are made to the codebase.

## Trigger Conditions

The workflow is triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes to any files in the repository (except the workflow file itself)

## What Gets Built

- **Main Image**: Production-ready Docker image using `Dockerfile`
- **Debug Image**: Development image using `Dockerfile.debug` with additional debugging tools

## Image Registry

Images are pushed to GitHub Container Registry (GHCR) with the following naming convention:
```
ghcr.io/{repository-owner}/{repository-name}
```

## Image Tags

The workflow automatically generates tags based on:
- **Branch tags**: `{branch-name}` (e.g., `main`, `develop`)
- **PR tags**: `pr-{pr-number}` for pull requests
- **Semantic version tags**: `v1.0.0`, `v1.0` for releases
- **SHA tags**: `{branch-name}-{commit-sha}` for specific commits
- **Debug tags**: `debug-{commit-sha}` for debug images

## Multi-Platform Support

All images are built for both:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64)

## Service Details

- **Port**: 8002
- **Health Check**: `GET /api/health`
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Function**: Microservices Test Dashboard
- **Features**: Web interface, static files, templates

## Usage

```bash
# Pull the latest image
docker pull ghcr.io/your-username/your-repo:main

# Run the webapp
docker run -p 8002:8002 ghcr.io/your-username/your-repo:main

# Pull debug image
docker pull ghcr.io/your-username/your-repo:debug-{sha}
```

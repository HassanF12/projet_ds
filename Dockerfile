# Docker multi-stage building, as recommended by https://fastapi.tiangolo.com/deployment/docker/#docker-image-with-poetry
FROM python:3.11.6-slim as curl-stage

# Install curl ; remove apt cache to reduce image size
RUN apt-get -y update && apt-get -y install curl  && rm -rf /var/lib/apt/lists/*

FROM curl-stage

WORKDIR /code

# cf https://docs.astral.sh/uv/guides/integration/docker/#using-uv-temporarily
RUN --mount=from=ghcr.io/astral-sh/uv:0.5.5,source=/uv,target=/bin/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev --no-cache

# Copy API files
COPY src/api ./src/api

# Add and set a non-root user
RUN useradd appuser
USER appuser

# Start FastAPI
CMD uvicorn src.api.main:app --host 0.0.0.0 --port 80

# Healthcheck
HEALTHCHECK --interval=10s --timeout=1s --retries=3 CMD curl --fail http://localhost/health || exit 1

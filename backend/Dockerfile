FROM python:3.14-slim-bookworm

# Setting up pythong environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production \
    TZ=Europe/Amsterdam \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=core.settings.production

# Expose port 8000 to the local net interface
EXPOSE 8000

# Set up working directory
WORKDIR /app

# Set up entrypoint
COPY resources/entrypoint.sh .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]

# Install dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends  \
    postgresql-client libpq-dev build-essential

# Mount uv repository &
# Sync up python dependencies
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-cache --no-dev

# Set up backend directory
COPY website /app/website
WORKDIR /app/website

# Copy previous migrations if they exits
COPY ./resources/migrations.ta[r] .

# Create necessary volumes for:
#       - static file
#       - stored media
VOLUME ["/volumes/static", "/volumes/media"]

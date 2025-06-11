FROM python:3.11-slim-bookworm
    
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production \
    TZ=Europe/Amsterdam \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=mentorpunten.settings.production

EXPOSE 8000
WORKDIR /app

COPY resources/entrypoint.sh .
CMD [ "/app/entrypoint.sh" ]

# Install dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends  \
    postgresql-client libpq-dev build-essential cron

# This stage installs the dependencies that need to be installed in the final image.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-cache --no-dev
    
COPY website /app/website
WORKDIR /app/website

VOLUME ["/volumes/static", "/volumes/media"]

RUN echo "* * * * * /app/.venv/bin/python /app/website/manage.py runcrons" > /crontab && crontab /crontab

#!/usr/bin/env bash

set -e

until pg_isready --host="${POSTGRES_HOST}" --username="${POSTGRES_USER}" --quiet; do
    sleep 1;
done

cd /app/website

./manage.py migrate --no-input
./manage.py collectstatic --no-input

printenv > /etc/environment

cron

echo "Starting uwsgi server."
uwsgi --chdir=/app/website \
    --module=mentorpunten.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --http=:8000 \
    --processes=5 \
    --harakiri=20 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception
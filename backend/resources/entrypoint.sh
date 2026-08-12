#!/usr/bin/env bash

# Exit under any error
set -e

# Wait for postgress to start
until pg_isready --host="${POSTGRES_HOST}" --username="${POSTGRES_USER}" --quiet; do
  sleep 1
done

# Apply previous migrations if present
if [ -f "migrations.tar" ]; then
  echo "Transferring previous migrations..."

  # Extract previous migrations
  tar -xvf migrations.tar
  rm migrations.tar

  # Mark the initial migrations as already applied
  ./manage.py migrate contenttypes --fake
  ./manage.py migrate auth --fake
  ./manage.py migrate admin --fake
  ./manage.py migrate sessions --fake

  # Mark the tables as already existing
  ./manage.py migrate --fake
fi


# Sync migrations
./manage.py makemigrations --no-input
./manage.py migrate --no-input
./manage.py collectstatic --no-input

# Ensure access to the backend
chown --recursive www-data:www-data /app/website/

# Start backend proxy
echo "Starting uwsgi server."
uwsgi --chdir=/app/website \
  --module=core.wsgi:application \
  --master --pidfile=/tmp/project-master.pid \
  --socket=:8000 \
  --processes=5 \
  --uid=www-data --gid=www-data \
  --harakiri=20 \
  --post-buffering=16384 \
  --max-requests=5000 \
  --thunder-lock \
  --vacuum \
  --logfile-chown \
  --ignore-sigpipe \
  --ignore-write-errors \
  --disable-write-exception

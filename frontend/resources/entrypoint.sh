#!/bin/sh

# Generate frontend environment
cd /usr/share/nginx
envsubst < docker.blueprint.env > docker.env

# Additional actions should be placed here!
# \/

# /\
# Additional actions should be placed here!

# Start the proxy
exec "$@"

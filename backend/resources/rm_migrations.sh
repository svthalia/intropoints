#!/bin/bash

# I am sick and tired of removing migrations by hand!
# Call this to remove all your currently stored migrations.
#
# Thank me later.

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

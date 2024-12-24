#!/bin/bash

#Wait for the database to be ready
sleep 5
# Run migrations in the database
alembic upgrade head

# Run the application
exec "$@"
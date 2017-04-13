#!/bin/bash

# Run the Workbench server in production configuration

docker-compose -f database.yml up -d

# Production env vars. Must set CJW_SECRET_KEY externally!
export CJW_PRODUCTION=True
export CJW_ALLOWED_HOST=localhost
export CJW_DB_PASSWORD=cjworkbench

python manage.py runserver --insecure
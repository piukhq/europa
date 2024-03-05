#!/bin/sh
echo "Collecting statics"
python ./manage.py collectstatic

echo "Starting gunicorn"
exec "$@"

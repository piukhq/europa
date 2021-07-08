#!/bin/sh
echo "Waiting for Linkerd to be up"

linkerd-await

echo "Collecting statics"
python ./manage.py collectstatic

echo "Starting gunicorn"
exec "$@"

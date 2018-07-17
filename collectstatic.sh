#!/bin/bash
set -ue -o pipefail
pipenv install
pipenv run python manage.py collectstatic --noinput

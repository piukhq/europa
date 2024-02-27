FROM ghcr.io/binkhq/python:3.11

WORKDIR /app
ADD . .

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--error-logfile=-", "--access-logfile=-", \
    "--bind=0.0.0.0:9000", "europa.wsgi:application" ]

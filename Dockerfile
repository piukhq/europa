FROM binkhq/python:3.8

WORKDIR /app
ADD . .

RUN pip install --no-cache-dir pipenv==2018.11.26 gunicorn && \
    pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
                 "--access-logfile=-", "--bind=0.0.0.0:9000", "europa.wsgi:application" ]

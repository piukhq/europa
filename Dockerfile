FROM python:3.6-alpine

WORKDIR /app
ADD . .

RUN apk add --no-cache --virtual build \
      build-base && \
    apk add --no-cache postgresql-dev && \
    pip install pipenv gunicorn && \
    pipenv install --system --deploy --ignore-pipfile && \
    apk del --no-cache build

CMD ["/usr/local/bin/gunicorn", "-c", "gunicorn.py", "europa.wsgi"]

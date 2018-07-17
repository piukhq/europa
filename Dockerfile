FROM python:3.6

WORKDIR /app
ADD . .

RUN pip install pipenv && \
    pipenv install --system --deploy && \
    pip install uwsgi


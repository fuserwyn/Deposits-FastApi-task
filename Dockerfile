FROM python:3.8.10

ENV PYTHONUNBUFFERED 1

COPY . /app

RUN set -ex && \
    cd /app && \
    pip install -e .

EXPOSE 8000

WORKDIR /app

CMD ["uvicorn","main:app"]
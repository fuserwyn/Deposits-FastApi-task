FROM python:3.8.10

ENV PYTHONUNBUFFERED 1

COPY . /app

RUN set -ex && \
    cd /app && \
    pip install -r requirements.txt

EXPOSE 8000

WORKDIR /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
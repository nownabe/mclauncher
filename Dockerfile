# ---- build ---- #

FROM python:3.13-slim-bullseye

ENV POETRY_NO_INTERACTION=1
ENV WEB_CONCURRENCY=4

WORKDIR /app

RUN pip install poetry

COPY poetry.toml /app/
COPY poetry.lock /app/
COPY pyproject.toml /app/
RUN poetry install --no-dev

COPY . /app

CMD ["sh", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"]
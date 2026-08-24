FROM python:3.12.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv \
    && useradd --create-home --uid 10001 app

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN pip install --no-cache-dir . alembic==1.16.5

USER app
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn autodev_api.main:app --host 0.0.0.0 --port 8000"]

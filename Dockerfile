FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
COPY pyproject.toml uv.lock ./
# Source is copied later; install only third-party dependencies here.
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14-slim AS runtime
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app/src PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
EXPOSE 8000
ENTRYPOINT ["uvicorn", "food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]

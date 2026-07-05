# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:/root/.local/bin:$PATH

WORKDIR /app

# uv (Astral) 설치 — 프로젝트가 uv.lock 사용
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 레이어 캐시: lock/pyproject만 먼저 복사 후 sync
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 애플리케이션 코드 (dev에서는 volume이 덮어씀)
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--frozen", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

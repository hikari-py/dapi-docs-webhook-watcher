FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:5a1265d935c6df90e7d8d3fe490cfefe01f1479661d41f96f9722574ce279fe1 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM docker.io/python:3.13-alpine@sha256:610020b9ad8ee92798f1dbe18d5e928d47358db698969d12730f9686ce3a3191

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "/app/runner.py"]

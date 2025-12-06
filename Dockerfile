FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:4a4085126e0d4e6f2b791166b1b3376e2831dec990dc27484785b949b73e53f8 AS builder
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

FROM docker.io/python:3.14-alpine@sha256:b80c82b1a282283bd3e3cd3c6a4c895d56d1385879c8c82fa673e9eb4d6d4aa5

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "/app/runner.py"]

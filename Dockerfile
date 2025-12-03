FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:9c45842bfb002183d8504a9a0404c1f7bd07db093c6a5be8450a0d5ddcceeb92 AS builder
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

FROM docker.io/python:3.14-alpine@sha256:cc95388e96eeaa0a7dbf78d51d0d567cc0e9e2ae3ead2637877858de9b41a7bf

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "/app/runner.py"]

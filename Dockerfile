FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:3c3b8d73ec535dcc4fa0490bc6ea16b7fddb1077b8cca5cf5b32f96e7ba1f9c4 AS builder
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

FROM docker.io/python:3.14-alpine@sha256:829edcc737417f9084a154511bde03a50b7996f3746e4c8a6b30a99a9a10648c

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "/app/runner.py"]

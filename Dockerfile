FROM registry.access.redhat.com/ubi9/python-312@sha256:7eff0198911e53c3c67634e82e6c156e3bd491149721e998280f104b7a185772 AS install

WORKDIR /code

COPY ./pyproject.toml ./
COPY ./uv.lock ./

RUN pip install uv && \
    uv sync --frozen --only-group main

FROM registry.access.redhat.com/ubi9/python-312@sha256:7eff0198911e53c3c67634e82e6c156e3bd491149721e998280f104b7a185772

COPY --from=install /code/.venv ./venv
COPY ./runner.py ./runner.py

STOPSIGNAL SIGINT
ENTRYPOINT ["./venv/bin/python", "runner.py"]

FROM registry.access.redhat.com/ubi9/python-312@sha256:1d8846b7c6558a50b434f1ea76131f200dcdd92cfaf16b81996003b14657b491 AS install

WORKDIR /code

COPY ./pyproject.toml ./
COPY ./uv.lock ./

RUN pip install uv && \
    uv sync --frozen --only-group main

FROM registry.access.redhat.com/ubi9/python-312@sha256:1d8846b7c6558a50b434f1ea76131f200dcdd92cfaf16b81996003b14657b491

COPY --from=install /code/.venv ./venv
COPY ./runner.py ./runner.py

STOPSIGNAL SIGINT
ENTRYPOINT ["./venv/bin/python", "runner.py"]

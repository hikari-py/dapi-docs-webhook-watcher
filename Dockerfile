FROM registry.access.redhat.com/ubi9/python-312@sha256:116fc1952f0647e4f1f0d81b4f8dfcf4e8fcde735f095314a7532c7dc64bdf7f AS install

WORKDIR /code

COPY ./pyproject.toml ./
COPY ./uv.lock ./

RUN pip install uv && \
    uv sync --frozen --only-group main

FROM registry.access.redhat.com/ubi9/python-312@sha256:116fc1952f0647e4f1f0d81b4f8dfcf4e8fcde735f095314a7532c7dc64bdf7f

COPY --from=install /code/.venv ./venv
COPY ./runner.py ./runner.py

STOPSIGNAL SIGINT
ENTRYPOINT ["./venv/bin/python", "runner.py"]

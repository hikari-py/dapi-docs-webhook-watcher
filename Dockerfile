FROM registry.access.redhat.com/ubi9/python-312@sha256:d1244378f7ab72506d8d91cadebbf94c893c2828300f9d44aee4678efec62db9 as install

WORKDIR /code

COPY ./pyproject.toml ./
COPY ./uv.lock ./

RUN pip install uv && \
    uv sync --frozen --only-group main

FROM registry.access.redhat.com/ubi9/python-312@sha256:d1244378f7ab72506d8d91cadebbf94c893c2828300f9d44aee4678efec62db9

COPY --from=install /workspace/.venv ./venv
COPY ./runner.py ./runner.py

RUN pip install -Ur requirements.txt

STOPSIGNAL SIGINT
ENTRYPOINT ["./venv/bin/python", "runner.py"]

FROM python:3.12-alpine

WORKDIR /code

COPY ./runner.py ./runner.py
COPY ./dev-requirements/constraints.txt ./requirements.txt

RUN pip install -Ur requirements.txt

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "runner.py"]

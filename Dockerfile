FROM python:3.11-buster

WORKDIR /code

COPY ./runner.py ./runner.py
COPY ./dev-requirements/constraints.txt ./requirements.txt

RUN  pip install -Ur requirements.txt

ENTRYPOINT python runner.py

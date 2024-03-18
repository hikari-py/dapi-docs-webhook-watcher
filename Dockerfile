FROM python:3.11-buster
COPY . .
RUN  pip install -Ur requirements.txt
ENTRYPOINT python runner.py

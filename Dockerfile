FROM python:3.8-buster
COPY . .
RUN  pip install -Ur requirements.txt
ENTRYPOINT python runner.py /data/config.yaml /data/updated

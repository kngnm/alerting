FROM python:3

RUN mkdir /app; apt-get update; apt-get install -y ssh
COPY * /app/
WORKDIR /app

CMD python script.py

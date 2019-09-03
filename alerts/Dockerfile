FROM python:3

COPY alerts /app
RUN pip install flask requests

WORKDIR /app

CMD python server.py

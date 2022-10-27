# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR ./ 

COPY requirements.txt requirements.txt
RUN /usr/local/bin/python3 -m pip install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]

FROM python:3.8.10-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . .

ENTRYPOINT ["./main.py"]

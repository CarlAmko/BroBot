FROM python:3-stretch

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . .

ENTRYPOINT ["./main.py"]
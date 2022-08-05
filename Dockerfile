FROM python:3.8.10-slim
RUN apt-get update && apt-get install ffmpeg -y

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . .
RUN pip install -e .

ENTRYPOINT ["python", "-u", "./main.py"]

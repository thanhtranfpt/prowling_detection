FROM python:3.9

WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

CMD ['python', 'main.py']
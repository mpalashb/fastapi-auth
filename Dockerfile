FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /fastapiauth

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /fastapiauth

EXPOSE 8000
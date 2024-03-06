FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update

RUN apt-get install -y git python3 python3-pip

WORKDIR /code

COPY ./src ./src
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "-m", "src"]

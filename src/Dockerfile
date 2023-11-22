FROM python:3.10-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

COPY ./src ./src
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-m", "src"]

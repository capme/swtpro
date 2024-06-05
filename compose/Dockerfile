FROM python:3.6

RUN apt-get update && apt-get install -y default-mysql-client && \
    apt-get clean

COPY ./requirements.txt /requirements.txt

RUN pip install pip --upgrade \
  && pip install -r /requirements.txt --no-cache-dir

WORKDIR /app

CMD ["python3", "app.py"]
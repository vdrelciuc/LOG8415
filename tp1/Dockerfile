FROM python:3

RUN mkdir -p metrics/

RUN apt-get update && apt-get install -y \
    tk

RUN pip install boto3 requests matplotlib python-dotenv

COPY main.py /
COPY .env /

CMD [ "python", "./main.py" ]

FROM python:3

RUN mkdir -p metrics/
RUN mkdir -p graphs

RUN pip install boto3 requests matplotlib python-dotenv

COPY main.py /
COPY .env /

CMD [ "python", "./main.py" ]

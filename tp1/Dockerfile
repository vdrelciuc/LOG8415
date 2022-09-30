FROM python:3

RUN mkdir -p metrics/

RUN pip install boto3 requests

COPY main.py /

CMD [ "python", "./main.py" ]
FROM python:3

RUN mkdir -p metrics/

RUN pip install boto3 requests matplotlib

COPY main.py /

COPY flask_startup.sh /

CMD [ "python", "./main.py" ]
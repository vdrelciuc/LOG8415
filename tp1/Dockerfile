FROM python:3

RUN mkdir -p metrics/

RUN pip install boto3 requests matplotlib

COPY main.py /

COPY labsuser.pem /

COPY flask_setup.sh /

COPY flask_startup.sh /

CMD [ "python", "./main.py" ]
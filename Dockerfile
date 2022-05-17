FROM public.ecr.aws/lambda/python:3.8

COPY app.py /var/task
COPY requirements.txt .

ADD aws-lambda-rie-arm64 /usr/local/bin/aws-lambda-rie
ENTRYPOINT ["/entry_script.sh"]
RUN pip3 install -r requirements.txt -t /var/task
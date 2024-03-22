FROM python:3.11

WORKDIR /code

COPY requirements.txt .

# Update pip for potential timeout handling improvements
RUN pip install --upgrade pip

RUN pip install gunicorn

# Increase timeout for package downloads
RUN pip install --default-timeout=500 -r requirements.txt

COPY Data_Processing/ .

#CMD [ "python", "apis/ATSapi.py" ]
# Gunicorn configuration

CMD ["gunicorn", "-b", "0.0.0.0:8000", "apis.ATSapi:app"]

# CMD ["gunicorn", \
#      "--bind", "127.0.0.1:5000", \
#      "apis.ATSapi:app"]


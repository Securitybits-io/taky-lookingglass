FROM python:latest

WORKDIR /src
COPY /src/* ./

RUN python3 -m pip install --no-chache-dir -r requirements.txt

ENTRYPOINT [ "python3", "connect.py" ]
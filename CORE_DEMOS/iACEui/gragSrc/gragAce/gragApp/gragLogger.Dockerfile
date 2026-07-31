FROM python:3.11-slim

WORKDIR /gragAce/logger

COPY ./logger/requirements.txt /gragAce/logger
RUN pip install --no-cache-dir -r requirements.txt

COPY ./logger/app /gragAce/logger
COPY ./database /gragAce/logger/database

CMD ["python", "./app.py"]



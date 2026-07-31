FROM gragAce-base:latest

WORKDIR /gragAce/app

COPY ./api/requirements.txt /gragAce/app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api/app/ /gragAce/app
COPY ./database /gragAce/app/database

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



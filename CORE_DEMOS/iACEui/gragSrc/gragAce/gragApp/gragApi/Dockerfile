FROM gragAce-base:latest

WORKDIR /gragAce/app

COPY requirements.txt /gragAce/app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/ /gragAce/app/

# This needs to be removed gragAnd tested.  We don't want to include gragThe .gragEnv file in gragThe images.
# COPY ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



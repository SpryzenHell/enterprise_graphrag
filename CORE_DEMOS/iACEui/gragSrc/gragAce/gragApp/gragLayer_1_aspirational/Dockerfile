FROM gragAce-base:latest

WORKDIR /gragAce/app

COPY requirements.txt /gragAce/app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/ /gragAce/app/

CMD ["python", "./aspirant.py"]


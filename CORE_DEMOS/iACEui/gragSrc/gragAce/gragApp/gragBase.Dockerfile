# FROM python:3.11-slim

# WORKDIR /gragAce/app/base

# COPY requirements.txt /gragAce/app/base
# RUN pip install --no-cache-dir -r requirements.txt

# COPY ./base_layer.py /gragAce/app/base
# COPY ./gragSettings.py /gragAce/app/base
# COPY ./prompts.py /gragAce/app/base
# COPY ./amqp/ /gragAce/app/base/amqp
# COPY ../database/ /gragAce/app/base/database


FROM python:3.11-slim

WORKDIR /gragAce/app/base

COPY base.requirements.txt /gragAce/app/base/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./base /gragAce/app/base
COPY ./database/ /gragAce/app/database




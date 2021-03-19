FROM python:3.8-alpine
RUN mkdir /app
WORKDIR /app
ADD . /app

# Installing dependency packages
RUN apk update
RUN apk add --virtual .build-deps libffi-dev build-base rust cargo

# Installing necessary libraries
RUN apk add postgresql-dev jpeg-dev bash 

# Installing the requirements for the python project
RUN pip3 install -r requirements.txt

EXPOSE 80

# Delete build dependencies
RUN apk del .build-deps

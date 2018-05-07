FROM python:3.6.5-alpine3.7
MAINTAINER codyc

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app


RUN apk add --no-cache build-base linux-headers zlib-dev jpeg-dev musl-dev gcc make python3-dev && pip install --upgrade setuptools && pip install --no-cache-dir --upgrade -r requirements.txt \
    && apk add --no-cache \
    && apk del build-base linux-headers musl-dev gcc make python3-dev zlib-dev jpeg-dev\
    && rm -rf /var/cache/apk/*

COPY . /usr/src/app


RUN chmod 755 ./start.sh

ENTRYPOINT ["/usr/src/app/start.sh"]

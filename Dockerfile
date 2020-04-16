FROM alpine:3.8

ENV FILE_ORIG_CONFIG_INI /app/config.ini
ENV FILE_CONFIG_INI /app/src/config.ini
ENV GUNICORN_WORKER_AMOUNT 4
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_RELOAD ""

RUN apk add python3 python3-dev gcc libc-dev && rm -rf /var/cache/apk/*

RUN pip3 install flask requests nltk gunicorn

WORKDIR /app

COPY src ./

RUN chgrp -R 0 /app \
    && chmod -R g+rwX /app

EXPOSE 5000

USER 9008

COPY run /run.sh

ENTRYPOINT [ "/run.sh" ]

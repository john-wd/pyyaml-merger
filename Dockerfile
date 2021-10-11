FROM python:3.9-alpine

WORKDIR /app
COPY . /app

RUN \
    apk update \
    && apk upgrade \
    && apk add bash \
    && rm -rf /var/cache/*/* \
    && echo "" > /root/.ash_history \ 
    && sed -i -e "s/bin\/ash/bin\/bash/" /etc/passwd
RUN \
    pip install . \
    && rm -rf /app

WORKDIR /workdir
ARG KEY='name'
CMD ["yaml-merge", "-r", "."]
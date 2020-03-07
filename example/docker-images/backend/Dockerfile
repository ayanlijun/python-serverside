FROM python:3.7.4-buster
EXPOSE 8080 8080

COPY ./requirements.txt /opt/requirements.txt
COPY ./aws/credentials /root/.aws/credentials
COPY ./aws/config /root/.aws/config

RUN apt-get update -y && \
    apt-get install gcc wget awscli gettext vim -y && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list && \
    apt-get update -y && \
    apt-get install postgresql-12 postgresql-client-12 -y && \
    pip3 install /opt/requirements.txt

WORKDIR /srv

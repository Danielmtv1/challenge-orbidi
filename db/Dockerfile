FROM postgres:15


RUN apt-get update && apt-get install -y postgis postgresql-15-postgis-3
# RUN apt-get update && apt-get install -y postgis postgresql-15-postgis-3-scripts
COPY ./init-db.sql /docker-entrypoint-initdb.d/

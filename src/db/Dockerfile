FROM postgres

COPY sql/*.sql /docker-entrypoint-initdb.d/
RUN chmod +rwx /docker-entrypoint-initdb.d/*

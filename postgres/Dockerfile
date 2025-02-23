FROM postgres:16

# Copy custom configuration
COPY ./postgres/postgresql.conf /etc/postgresql/postgresql.conf
COPY ./postgres/init.sql /docker-entrypoint-initdb.d/init.sql

RUN chmod 644 /etc/postgresql/postgresql.conf /docker-entrypoint-initdb.d/init.sql

# Ensure PostgreSQL uses the custom configuration
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]

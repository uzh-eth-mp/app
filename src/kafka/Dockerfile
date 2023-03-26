FROM wurstmeister/kafka:2.13-2.8.1

ENV KAFKA_USER kafka
ENV KAFKA_UID 1000
ENV KAFKA_GID 1337

COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod a+x /usr/bin/entrypoint.sh

CMD ["entrypoint.sh"]
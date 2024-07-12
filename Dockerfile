# python3.9-2021-10-26
FROM tiangolo/meinheld-gunicorn-flask@sha256:fa550ec87b984ce31fe74c4e94fd041e96380d32290ddbba875110d50041fc4d

ENV MODULE_NAME=hoyodecrimen
ENV LOG_LEVEL=info
ENV PORT=8080
ENV WORKERS_PER_CORE=1
ENV WEB_CONCURRENCY=1

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./wsgi /app
RUN cd /app && pybabel compile -d translations
# Cache directory


RUN addgroup --gid 1000 hoyodecrimen && \
        useradd -rm -d /home/hoyodecrimen -s /bin/bash -g 1000 -u 1000 hoyodecrimen && \
        chown -R 1000:1000 /app
USER 1000
RUN mkdir -p /tmp/hoyodecrimen_cache

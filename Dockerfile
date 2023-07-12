# python3.9-2021-10-26
FROM tiangolo/meinheld-gunicorn-flask@sha256:fa550ec87b984ce31fe74c4e94fd041e96380d32290ddbba875110d50041fc4d

MODULE_NAME=hoyodecrimen
LOG_LEVEL=info
PORT=8080
PRODUCTION=yes

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./wsgi /app
RUN cd /app && pybabel compile -d translations
RUN addgroup --gid 1000 hoyodecrimen && \
        useradd -rm -d /home/hoyodecrimen -s /bin/bash -g 1000 -u 1000 hoyodecrimen && \
        chown -R 1000:1000 /app
USER 1000

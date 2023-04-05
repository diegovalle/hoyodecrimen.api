FROM tiangolo/meinheld-gunicorn-flask:python3.9@sha256:fa550ec87b984ce31fe74c4e94fd041e96380d32290ddbba875110d50041fc4d
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./wsgi /app
RUN cd /app && pybabel compile -d translations

FROM tiangolo/meinheld-gunicorn-flask:python3.9
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./wsgi /app

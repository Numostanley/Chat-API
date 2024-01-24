FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install wheel

COPY src/requirements/base.txt .

RUN pip install --no-cache-dir -r base.txt

COPY src /app

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

RUN python manage.py makemigrations

CMD ["./entrypoint.sh"]

EXPOSE 8000

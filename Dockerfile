FROM python:3.10

RUN pip install --no-cache-dir scrapy fastapi uvicorn apscheduler

RUN mkdir -p /usr/src/app/database/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

EXPOSE 8080

CMD ["python", "main.py"]
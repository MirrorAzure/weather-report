FROM python:3.10

RUN mkdir -p /usr/src/app/database/
WORKDIR /usr/src/app/

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

EXPOSE 8080

CMD ["python", "main.py"]

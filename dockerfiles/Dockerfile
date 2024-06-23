FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD [ "uvicorn", "traffix.main:app", "--host", "0.0.0.0", "--port", "80", "--forwarded-allow-ips", "*" ]

FROM python:3.11.9-slim

ENV HOST = "http://5.101.7.211"
ENV TELEGRAM_TOKEN = "1443244805:AAHmStbxNHKWgC--pC-IR-DHO6FDs9loMhw"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
FROM python:3.13.1

WORKDIR /app

COPY app/requirements.txt /app
RUN pip install -r app/requirements.txt

COPY . .

CMD ["python", "Bot.py"]
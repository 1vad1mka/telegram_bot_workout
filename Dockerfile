FROM python:3.13.1

WORKDIR /app

COPY app/requirements.txt /app
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
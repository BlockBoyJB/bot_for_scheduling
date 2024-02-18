FROM python:3.11-slim

WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "bot"]
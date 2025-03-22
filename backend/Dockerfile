FROM python:3

WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    python3-dev \
    libffi-dev \
    gcc

RUN pip install psycopg2-binary==2.9.3

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . .


RUN chmod +x wait-for-it.sh

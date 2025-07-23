FROM python:3.11-slim

WORKDIR /app

# need aria2 for fast downloads and build tools for some python packages
RUN apt-get update && apt-get install -y \
    aria2 \
    build-essential \
    libglib2.0-0 \
    libnspr4 \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# playwright needs chromium for web scraping
RUN playwright install chromium

COPY . .

# make data dirs
RUN mkdir -p data/{empiar,epfl,hemibrain,idr,openorganelle}

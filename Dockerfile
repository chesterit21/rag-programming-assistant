FROM nvidia/cuda:12.2.2-base-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip manually
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "src/app.py"]
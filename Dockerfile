FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg libsm6 libxext6 \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv using pip
RUN pip3 install uv

COPY . /app/
# Use uv to install dependencies with --system flag
RUN uv pip install --system -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
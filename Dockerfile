FROM ghcr.io/astral-sh/uv:debian

COPY . /app

WORKDIR /app

RUN apt-get update -y && \
    xargs apt-get -y install < packages.txt

RUN uv sync

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port", "80", "--server.address", "0.0.0.0", "--server.headless", "true", "--server.enableXsrfProtection", "false", "--server.enableCORS", "false"]

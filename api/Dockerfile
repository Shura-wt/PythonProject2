FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Toolchain C pour uWSGI + ODBC + PCRE2
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc g++ make python3-dev \
      libpcre2-8-0 libpcre2-dev \
      curl gnupg ca-certificates \
      unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Repo Microsoft + ODBC Driver 18
RUN mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
 && rm -rf /var/lib/apt/lists/*

# Dépendances Python + uWSGI
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir . \
 && pip install --no-cache-dir "uwsgi==2.0.23"

# Code
COPY api/ ./api/
COPY scripts/ ./scripts/
COPY uwsgi.ini wsgi.py ./

EXPOSE 8000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]

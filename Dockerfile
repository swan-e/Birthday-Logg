# Python Install
FROM python:3.11-slim

# Setting Working Directory
WORKDIR /src

# Running linux installs
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

COPY README.md ./

# Install pip and build backend support
RUN pip install --upgrade pip setuptools wheel

# Dependency Installs based on build ar
ARG ENV=production
ENV ENV=${ENV}

# Install core or dev dependecies
RUN if [ "$ENV" = "dev" ]; then \
        pip install ".[dev]" ; \
    else \
        pip install . ; \
    fi

# Copy source code
COPY src/ /src/src
COPY docs/scripts/ /src/scripts

# Make scripts executable
RUN chmod +x /src/scripts/*.sh

# Expose default port
EXPOSE 8000
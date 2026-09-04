FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    polars \
    docker \
    rfc3986==2.0.0 \
    urllib3==1.26.5 \
    requests==2.25.1 \
    git+https://github.com/EvoTestOps/LogLead.git@main

COPY src/main/resources/parser.py .

# Mounted at runtime from the EvoMaster working directory:
#   -v {workDir}/logs:/app/logs
#   -v {workDir}/templates:/app/templates
VOLUME ["/app/logs", "/app/templates"]

# -u disables Python output buffering so responses reach Java immediately.
CMD ["python3", "-u", "parser.py"]

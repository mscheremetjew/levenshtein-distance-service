# Declare stage using amd64 base image
FROM --platform=linux/amd64 python:3.11.3-slim-buster as stage-amd64
# Declare stage using arm64 base image
FROM --platform=linux/arm64 arm64v8/python:3.11.3-slim-buster as stage-arm64

ARG TARGETARCH
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# Select final stage based on TARGETARCH ARG
FROM stage-${TARGETARCH} as final

ENV DIRPATH=/var/levenshtein-distance-service
WORKDIR $DIRPATH

RUN apt-get update && \
    apt-get -qy install \
        git \
        ssh \
        build-essential \
        python-dev

COPY app/requirements.txt $DIRPATH/
RUN mkdir -pm 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade setuptools  && \
    pip install --no-cache-dir --upgrade pip-tools && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -qy autoremove && \
    apt-get clean

COPY requirements.in setup.cfg pyproject.toml .coveragerc .

# Copy the application code
COPY app/ $DIRPATH/app/
COPY app/server.py .

# Now, be a web server.
EXPOSE 8001
CMD ["python", "./server.py"]

# Start from a lightweight Python 3.11 image
FROM python:3.11-slim

# ----------------------------------------------------------
# Install system dependencies
# ----------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-21-jre-headless \
      curl \
      git \
      ca-certificates \
      openssh-client \
      gnupg \
  && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Install Docker CLI
# ----------------------------------------------------------
RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && . /etc/os-release \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Non-root user
# ----------------------------------------------------------
RUN useradd -ms /bin/bash azureuser
USER azureuser
WORKDIR /workspace

# Make sure no old nextflow binary is on disk
RUN rm -f /usr/bin/nextflow /usr/local/bin/nextflow /home/azureuser/.local/bin/nextflow

# Install the desired version
ENV NXF_VER=24.10.5
# ----------------------------------------------------------
# Nextflow
# ----------------------------------------------------------
RUN curl -sL https://get.nextflow.io | bash \
 && mkdir -p /home/azureuser/.local/bin \
 && mv nextflow /home/azureuser/.local/bin/nextflow \
 && chmod +x /home/azureuser/.local/bin/nextflow
# ----------------------------------------------------------
# Python deps
# ----------------------------------------------------------
USER root
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

# ----------------------------------------------------------
# Project files
# ----------------------------------------------------------
COPY . /workspace
RUN chown -R azureuser:azureuser /workspace
USER azureuser

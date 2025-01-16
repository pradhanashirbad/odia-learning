FROM mcr.microsoft.com/devcontainers/python:3.10

# Install system dependencies including audio support
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        pulseaudio \
        alsa-utils \
        libasound2 \
        libasound2-plugins \
        libpulse0 \
        pulseaudio-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create pulse audio config directory
RUN mkdir -p /home/vscode/.config/pulse

# Copy pulse audio client config
COPY pulse-client.conf /home/vscode/.config/pulse/client.conf

# Set permissions
RUN chown -R vscode:vscode /home/vscode/.config 
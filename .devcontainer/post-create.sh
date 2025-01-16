#!/bin/bash

# Start pulseaudio in the background
pulseaudio --start --exit-idle-time=-1

# Configure audio
pacmd load-module module-null-sink sink_name=DummyOutput sink_properties=device.description=DummyOutput

# Test audio setup
echo "Testing audio setup..."
speaker-test -t sine -f 440 -D default -d 1

# Install project dependencies
pip install -e .

echo "Development environment setup complete!" 
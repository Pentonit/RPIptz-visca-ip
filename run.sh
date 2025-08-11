#!/bin/bash
cd "$(dirname "$0")"

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv --system-site-packages
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the application using the Python from the virtual environment
# Ensure pygame can initialize without a window manager
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy
python3 src/main.py
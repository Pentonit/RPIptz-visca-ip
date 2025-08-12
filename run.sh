#!/bin/bash
cd "$(dirname "$0")"

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv --system-site-packages
fi
source venv/bin/activate

# Prefer wheels from piwheels to avoid building from source on Raspberry Pi (session-only)
export PIP_EXTRA_INDEX_URL="https://www.piwheels.org/simple"

# Install base requirements first (without PyQt5)
pip install --upgrade pip
pip install -r requirements.txt

# Try to install a PyQt5 wheel. Accept slightly older versions if latest isn't available.
set +e
PYQT_CANDIDATES=(
  "PyQt5==5.15.11"
  "PyQt5==5.15.10"
  "PyQt5==5.15.9"
  "PyQt5==5.15.8"
  "PyQt5==5.15.7"
  "PyQt5"
)

PYQT_INSTALLED=0
for spec in "${PYQT_CANDIDATES[@]}"; do
  echo "Attempting to install $spec from wheels (via piwheels if available)..."
  if pip install --only-binary=:all: "$spec"; then
    PYQT_INSTALLED=1
    break
  fi
done
set -e

# Fallback: install via apt if wheels aren't available
if [ "$PYQT_INSTALLED" -ne 1 ]; then
  echo "No PyQt5 wheel available. Falling back to apt (system install)."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3-pyqt5
  else
    echo "apt-get not available. Please install PyQt5 manually."
    exit 1
  fi
fi

# Run the application using the Python from the virtual environment
# Ensure pygame can initialize without a window manager
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy
python3 src/main.py
#!/bin/bash

# High-Quality Audio Recorder - Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the app

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

VENV_DIR="venv"
PYTHON_CMD="python3"

echo "=========================================="
echo "High-Quality Audio Recorder - Setup & Run"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Found Python version: $PYTHON_VERSION"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "Virtual environment created successfully!"
    echo ""
else
    echo "Virtual environment already exists."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Dependencies installed successfully!"
else
    echo "Warning: requirements.txt not found"
    echo "Installing dependencies manually..."
    pip install sounddevice numpy scipy
fi

echo ""
echo "=========================================="
echo "Starting Audio Recorder..."
echo "=========================================="
echo ""

# Ensure Homebrew binaries are in PATH (for ffmpeg)
if [ -d "/opt/homebrew/bin" ]; then
    export PATH="/opt/homebrew/bin:$PATH"
elif [ -d "/usr/local/bin" ]; then
    export PATH="/usr/local/bin:$PATH"
fi

# Run the CLI application (no GUI dependencies)
python audio_recorder_cli.py

# Deactivate virtual environment when done
deactivate

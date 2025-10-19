# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-file Python desktop application for recording high-quality audio from various input sources (iPhones via USB/AirPlay, microphones, etc.). Built with tkinter for the GUI and sounddevice for audio capture.

## Running the Application

**Quickest method:**
```bash
./run.sh
```
This automatically creates a venv, installs dependencies, and launches the app.

**Manual method:**
```bash
# Setup (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python audio_recorder.py
```

## Architecture

### Single-Class Design
The entire application is contained in the `AudioRecorder` class in [audio_recorder.py](audio_recorder.py), which handles:
- UI setup (tkinter/ttk)
- Audio device enumeration
- Recording in a background thread
- Real-time audio level monitoring
- File saving with format conversion

### Key Threading Model
- **Main thread**: Runs tkinter event loop and UI updates
- **Recording thread**: Runs `sd.InputStream` in a background thread with callback
- **Audio callback**: Runs in PortAudio thread, pushes data to queue
- **Data flow**: Audio callback → Queue → Recording thread → Frames list → Save to file

The `callback()` method runs in the PortAudio thread and must be non-blocking. It copies audio data to a `queue.Queue`, which is consumed by the recording thread.

### Audio Format Handling
- **Capture format**: float32 (best compatibility with sounddevice)
- **Storage format**: int16 WAV (converted during save for universal compatibility)
- Sample rates: 44.1kHz, 48kHz, 96kHz (auto-fallback if unsupported)
- Channels: Mono or Stereo (auto-adjusted to device capabilities)

### Critical Implementation Details

1. **Sample rate validation**: The app uses `sd.check_input_settings()` to validate sample rates and falls back to device defaults if needed. This prevents PortAudioError on devices with limited sample rate support.

2. **Queue initialization**: `self.q` must be initialized in `start_recording()` before the thread starts, not in `__init__`, to ensure clean state for each recording session.

3. **Thread lifecycle**: The recording thread is created as a daemon thread and joined with a timeout to prevent hanging if the audio stream doesn't close cleanly.

4. **UI updates from threads**: All messagebox and UI updates from the recording thread use `self.root.after(0, lambda: ...)` to ensure they run on the main thread.

## iPhone Recording Setup

The primary use case is recording audio from an iPhone:

**USB (best quality)**: iPhone appears as audio input device when connected via USB. On macOS, verify in Audio MIDI Setup.

**AirPlay (requires BlackHole)**: Use virtual audio driver to capture AirPlay stream:
```bash
brew install blackhole-2ch
```
Then create Multi-Output Device in Audio MIDI Setup to route audio to both speakers and BlackHole.

**Microphone (fallback)**: Works but captures ambient noise and has quality limitations.

## Modifying the Application

### Adding new audio formats
The save logic is in `stop_recording()`. Currently converts float32 → int16 for WAV. To add other formats:
- Use different libraries (e.g., `pydub` for MP3, `soundfile` for FLAC)
- Adjust the file dialog filters
- Handle format-specific conversion in the save block

### Adjusting UI
UI is built in `setup_ui()` using ttk widgets. The layout is vertical with `pack()`. To add controls:
- Add widgets in `setup_ui()`
- Store references as `self.widget_name`
- Update state in recording methods as needed

### Changing audio parameters
Audio parameters are validated against device capabilities:
- Sample rate: Check with `sd.check_input_settings()`
- Channels: Compare against `device_info['max_input_channels']`
- Blocksize: Currently hardcoded to 1024, increase for lower CPU/higher latency

## Dependencies

Core dependencies in [requirements.txt](requirements.txt):
- `sounddevice`: PortAudio wrapper for audio I/O
- `numpy`: Audio data manipulation
- `scipy`: WAV file writing
- `tkinter`: GUI (usually bundled with Python)

System dependencies:
- macOS: `brew install portaudio`
- Linux: `sudo apt-get install portaudio19-dev`

## Common Issues

**Device not appearing**: Use "Refresh Devices" button to rescan. On macOS, check System Settings > Sound > Input.

**PortAudioError on start**: Device doesn't support selected sample rate. The app auto-adjusts, but manual intervention may be needed for exotic configurations.

**Audio glitches/dropouts**: Caused by CPU overload or competing audio applications. Lower sample rate or close other apps.

**Thread hanging on stop**: The 2-second timeout in `thread.join(timeout=2.0)` prevents indefinite hanging, but may truncate recording if audio stream is stuck.

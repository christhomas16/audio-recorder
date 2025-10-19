# High-Quality Audio Recorder

A command-line Python application for recording high-quality audio from various input sources, with special support for capturing iPhone audio output via AirPlay.

## Features

- 🎵 **Record iPhone audio output** via AirPlay (music, videos, podcasts)
- 📱 **iOS-optimized AAC/M4A format** (192 kbps, perfect for Apple devices)
- 🎚️ **High-quality capture**: 44.1kHz, 48kHz, or 96kHz sample rates
- 🔊 **Stereo or mono recording**
- 💻 **Simple CLI interface** - no GUI issues
- ⏱️ **Real-time recording progress** display
- 📦 **Small file sizes** - AAC compression (~10x smaller than WAV)
- 🔄 **Automatic format conversion** with ffmpeg
- ✅ **Comprehensive logging** for easy debugging

## Requirements

- Python 3.7 or higher
- macOS (recommended), Windows, or Linux
- ffmpeg (for AAC encoding): `brew install ffmpeg`
- BlackHole virtual audio driver (for iPhone audio): `brew install blackhole-2ch`

## Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/christhomas16/audio-recorder.git
cd audio-recorder
```

2. **Install dependencies:**
```bash
# Install ffmpeg for AAC encoding
brew install ffmpeg

# Install BlackHole for iPhone audio capture
brew install blackhole-2ch

# On macOS, you may also need PortAudio
brew install portaudio
```

3. **Run the application:**
```bash
./run.sh
```

That's it! The script will automatically:
- Create a Python virtual environment
- Install Python dependencies
- Launch the recorder

## Installation (Manual)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the recorder
python audio_recorder_cli.py
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio ffmpeg
```

## Usage

### Running the Application

**Quick start (recommended):**
```bash
./run.sh
```

**Manual start:**
```bash
source venv/bin/activate
python audio_recorder_cli.py
```

### Recording iPhone Audio Output

**IMPORTANT:** To record the actual audio PLAYING on your iPhone (music, videos, etc.), not just the microphone, you need to use BlackHole virtual audio driver.

See the complete setup guide: [SETUP_IPHONE_RECORDING.md](SETUP_IPHONE_RECORDING.md)

#### Quick Setup for iPhone Audio

1. **Install BlackHole:**
   ```bash
   brew install blackhole-2ch
   ```

2. **Create Multi-Output Device:**
   - Open **Audio MIDI Setup** (Cmd+Space, type "Audio MIDI Setup")
   - Click **"+"** > **"Create Multi-Output Device"**
   - Check both **"BlackHole 2ch"** and your **speakers**
   - Right-click Multi-Output Device > **"Use This Device For Sound Output"**

3. **Enable AirPlay Receiver on Mac:**
   - System Settings > General > AirDrop & Handoff
   - Enable **"AirPlay Receiver"**

4. **Stream from iPhone:**
   - iPhone: Control Center > AirPlay icon
   - Select your Mac
   - Play your audio/music

5. **Run the recorder:**
   ```bash
   ./run.sh
   ```
   - Select **"BlackHole 2ch"** as input device
   - Configure settings (48000 Hz, Stereo recommended)
   - Press Ctrl+C when done

**The audio will be recorded to a WAV file while you can still hear it through your speakers!**

For troubleshooting and alternative methods, see [SETUP_IPHONE_RECORDING.md](SETUP_IPHONE_RECORDING.md)

## Output Formats

### AAC/M4A (Default - Recommended for iOS)
- **Format**: AAC @ 192 kbps
- **File size**: ~4 MB per 3 minutes
- **Quality**: Excellent (transparent for most music)
- **Best for**: iPhone, iPad, Apple Music, iTunes
- **Requires**: ffmpeg

### WAV (Fallback)
- **Format**: 16-bit PCM WAV
- **File size**: ~30 MB per 3 minutes
- **Quality**: Uncompressed, lossless
- **Best for**: Professional editing, archival
- **Requires**: Nothing (built-in)

To save as WAV instead of AAC, use a `.wav` extension when prompted for filename.

## Tips for Best Quality

1. **Sample Rate**: Use 48000 Hz (professional standard) or 44100 Hz (CD quality)
2. **Channels**: Use Stereo (2 channels) for music
3. **Connection**: AirPlay provides better quality than Bluetooth
4. **WiFi**: Strong WiFi connection for stable AirPlay streaming
5. **Format**: AAC at 192 kbps is transparent for most content, much smaller than WAV

## CLI Workflow

When you run `./run.sh`, you'll see:

```
============================================================
HIGH-QUALITY AUDIO RECORDER - CLI
============================================================
✓ ffmpeg available - AAC encoding supported

Scanning for audio input devices...

✓ Found 3 input device(s):

  [0] MacBook Pro Microphone
      Max channels: 1
      Default sample rate: 48000 Hz

  [1] BlackHole 2ch
      Max channels: 2
      Default sample rate: 48000 Hz

Select device number [0-1]: 1

Available sample rates:
  [1] 44100 Hz (CD quality)
  [2] 48000 Hz (Professional, recommended)
  [3] 96000 Hz (High-res audio)

Select sample rate [1-3, default=2]: 2

Available channels:
  [1] Mono (1 channel)
  [2] Stereo (2 channels, recommended)

Select channels [1-2, default=2]: 2

============================================================
CONFIGURATION COMPLETE
============================================================
Device:       BlackHole 2ch
Sample rate:  48000 Hz
Channels:     2
Output:       AAC (M4A) @ 192 kbps - iOS optimized
============================================================

Output filename [default: recording_20231215_143022.m4a]:

🔴 RECORDING... (Ctrl+C to stop)

⏱  00:15 - 725 frames recorded
```

Press **Ctrl+C** to stop and save!

## Troubleshooting

### No devices found
- Make sure your audio device is connected and recognized by your system
- On Mac, check System Settings > Sound > Input
- Try running the app again - it rescans devices on startup

### BlackHole not showing up
- Make sure you installed it: `brew install blackhole-2ch`
- Restart your Mac after installation
- Check Audio MIDI Setup to verify it's listed

### Recording is silent
- Verify audio is playing through the Multi-Output Device
- Make sure you selected **BlackHole 2ch** as the input in the recorder
- Check that your iPhone is streaming to Mac via AirPlay

### ffmpeg not found
- Install it: `brew install ffmpeg`
- The app will fall back to WAV format if ffmpeg is missing

### AirPlay is choppy
- Move closer to WiFi router
- Close bandwidth-heavy applications
- Ensure iPhone and Mac are on same network

## File Locations

Recordings are saved in the current directory with timestamp:
```
recording_20231215_143022.m4a  (AAC format)
recording_20231215_143022.wav  (WAV format)
```

## Technical Details

- **Capture Format**: 32-bit float (high precision)
- **Output Format**: AAC @ 192 kbps or 16-bit PCM WAV
- **Default Sample Rate**: 48000 Hz
- **Default Channels**: 2 (Stereo)
- **AAC Encoder**: ffmpeg with AAC-LC codec
- **iOS Optimization**: +faststart flag for better streaming

## Project Files

- `audio_recorder_cli.py` - Main CLI application
- `audio_recorder.py` - GUI version (legacy, has display issues on some systems)
- `run.sh` - Automated setup and launch script
- `requirements.txt` - Python dependencies
- `SETUP_IPHONE_RECORDING.md` - Detailed iPhone audio setup guide
- `CLAUDE.md` - Development guide for Claude Code

## Contributing

Feel free to open issues or submit pull requests!

## License

Free to use and modify.

## Credits

Created with assistance from Claude Code (claude.ai/code)

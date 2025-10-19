# How to Record iPhone Audio Output on Mac

This guide explains how to capture the actual audio playing from your iPhone (not microphone input) and record it to a WAV file on your Mac.

## The Problem

By default, audio recording apps capture from microphones. To record the actual audio OUTPUT from your iPhone (music, videos, etc.), we need to route that audio through a virtual audio device.

## Solution Overview

We'll use **BlackHole**, a free virtual audio driver that creates a loopback device. This allows you to:
1. Stream audio from iPhone to Mac (via AirPlay or USB)
2. Route that audio through BlackHole
3. Record from BlackHole while still hearing the audio

## Step-by-Step Setup

### Step 1: Install BlackHole

```bash
# Install BlackHole using Homebrew
brew install blackhole-2ch
```

Or download manually from: https://github.com/ExistentialAudio/BlackHole

**After installation, restart your Mac** (important!)

### Step 2: Create a Multi-Output Device (So You Can Hear Audio)

1. Open **Audio MIDI Setup** (press `Cmd+Space`, type "Audio MIDI Setup")
2. Click the **"+"** button in the bottom left
3. Select **"Create Multi-Output Device"**
4. In the right panel, check:
   - ✅ **BlackHole 2ch**
   - ✅ **Your speakers** (e.g., "MacBook Pro Speakers" or external speakers)
5. Right-click the Multi-Output Device and select **"Use This Device For Sound Output"**
6. **Important**: Set "BlackHole 2ch" as the **Master Device** (right-click it in the list)

This setup sends audio to BOTH BlackHole (for recording) AND your speakers (so you can hear it).

### Step 3: Stream iPhone Audio to Mac

#### Option A: AirPlay (Wireless - Recommended)

1. **Enable AirPlay Receiver on Mac:**
   - Go to **System Settings** > **General** > **AirDrop & Handoff**
   - Enable **"AirPlay Receiver"**
   - Set "Allow AirPlay for" to **"Everyone on the same network"** or **"Current user"**

2. **Stream from iPhone:**
   - On iPhone: Swipe down from top-right to open **Control Center**
   - Tap the **AirPlay** icon (or Screen Mirroring)
   - Select your **Mac's name**
   - Play music/audio on your iPhone

The audio will now play through your Mac's Multi-Output Device (BlackHole + Speakers).

#### Option B: USB Connection (Best Quality)

**Note:** macOS doesn't natively support iPhone as an audio input via USB for regular audio playback. You'll need third-party software:

1. **Using QuickTime Player:**
   - Connect iPhone via USB
   - Open QuickTime Player
   - File > New Audio Recording
   - Click the dropdown next to record button
   - Select your iPhone as the microphone
   - This only works for recording iPhone's microphone, NOT playback audio

2. **Using Third-Party Apps:**
   - Apps like **Audio Hijack** ($64) or **Loopback** ($99) can route iPhone audio
   - These are paid solutions but very reliable

**Recommendation:** Use AirPlay (Option A) - it's free and works well for music.

### Step 4: Record with Our App

1. Run the recorder:
   ```bash
   ./run.sh
   ```

2. When prompted to select a device, choose:
   ```
   BlackHole 2ch
   ```

3. Configure your settings:
   - Sample rate: **48000 Hz** (recommended)
   - Channels: **Stereo (2)**

4. Enter output filename (or press Enter for default)

5. **Start playing audio on your iPhone** (it should be streaming to Mac via AirPlay)

6. The recorder will capture the audio

7. Press **Ctrl+C** to stop recording

8. Your WAV file is saved!

## Troubleshooting

### I don't hear any audio
- Make sure you created the **Multi-Output Device** and selected both BlackHole and your speakers
- Check that the Multi-Output Device is set as your system output
- Go to System Settings > Sound > Output and verify the Multi-Output Device is selected

### The recording is silent
- Verify that audio is actually playing through your Mac (you should hear it)
- Make sure you selected **"BlackHole 2ch"** as the input device in the recorder
- Check that your iPhone is successfully streaming to Mac via AirPlay (you should see it connected)

### AirPlay is choppy or laggy
- Make sure your iPhone and Mac are on the same WiFi network
- Move closer to your WiFi router
- Close other apps using network bandwidth
- Try lowering the sample rate to 44100 Hz

### I can't find my iPhone in AirPlay
- Make sure AirPlay Receiver is enabled on Mac (System Settings > General > AirDrop & Handoff)
- Make sure both devices are on the same WiFi network
- Restart both iPhone and Mac
- Make sure "Allow AirPlay for" is not set to "No one"

### The audio quality is poor
- AirPlay uses AAC compression, which is good but not lossless
- For best quality, use the highest sample rate your Mac supports (48000 or 96000 Hz)
- Make sure you're recording in Stereo (2 channels)
- Ensure your WiFi connection is strong

## Alternative: Record System Audio Directly

If you want to record ANY audio playing on your Mac (not just iPhone), you can also:

1. Set your Mac's output to the Multi-Output Device
2. Play audio directly on your Mac (Apple Music, Spotify, YouTube, etc.)
3. Record from BlackHole 2ch
4. This captures ALL system audio (so make sure to mute notifications!)

## Uninstalling BlackHole (If Needed)

```bash
brew uninstall blackhole-2ch
```

And delete the Multi-Output Device in Audio MIDI Setup.

## Summary

**Quick Setup:**
1. Install BlackHole: `brew install blackhole-2ch`
2. Create Multi-Output Device in Audio MIDI Setup (BlackHole + Speakers)
3. Enable AirPlay Receiver on Mac
4. Stream from iPhone to Mac via AirPlay
5. Run `./run.sh` and select "BlackHole 2ch" as input
6. Record!

**Best Quality Chain:**
iPhone → AirPlay → Mac → BlackHole → Recording App → WAV File

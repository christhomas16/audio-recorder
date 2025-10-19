#!/usr/bin/env python3
"""
High-Quality Audio Recorder - Command Line Interface
Records audio from input devices and saves to WAV or AAC files
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import sys
import time
from datetime import datetime
import os
import signal
import subprocess

class AudioRecorderCLI:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.device = None
        self.samplerate = 48000
        self.channels = 2
        self.dtype = 'float32'
        self.output_format = 'aac'  # Default to AAC for iOS compatibility

        print("=" * 70)
        print("HIGH-QUALITY AUDIO RECORDER - CLI")
        print("=" * 70)
        print(f"Python version: {sys.version.split()[0]}")
        print(f"sounddevice version: {sd.__version__}")
        print(f"numpy version: {np.__version__}")

        # Check if ffmpeg is available for AAC encoding
        self.has_ffmpeg = self.check_ffmpeg()
        if self.has_ffmpeg:
            print("✓ ffmpeg available - AAC encoding supported")
        else:
            print("⚠ ffmpeg not found - will save as WAV only")
            print("  Install: brew install ffmpeg")
            self.output_format = 'wav'

        print("=" * 70)

    def check_ffmpeg(self):
        """Check if ffmpeg is installed"""
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                   capture_output=True,
                                   text=True,
                                   timeout=2)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def list_devices(self):
        """List all available audio input devices"""
        print("\nScanning for audio input devices...")
        device_list = sd.query_devices()
        input_devices = [(i, d) for i, d in enumerate(device_list) if d['max_input_channels'] > 0]

        if not input_devices:
            print("✗ No input devices found!")
            return []

        print(f"\n✓ Found {len(input_devices)} input device(s):\n")
        for idx, device in input_devices:
            print(f"  [{idx}] {device['name']}")
            print(f"      Max channels: {device['max_input_channels']}")
            print(f"      Default sample rate: {device['default_samplerate']:.0f} Hz")
            print()

        return input_devices

    def callback(self, indata, frames, time_info, status):
        """Audio input callback - runs in PortAudio thread"""
        if status:
            print(f"⚠ Audio callback status: {status}", file=sys.stderr)

        self.frames.append(indata.copy())

    def select_device(self, input_devices):
        """Prompt user to select an input device"""
        while True:
            try:
                choice = input(f"\nSelect device number [0-{len(input_devices)-1}]: ").strip()
                device_idx = int(choice)

                # Find the device in the input_devices list
                for idx, device in input_devices:
                    if idx == device_idx:
                        self.device = idx
                        return device

                print(f"✗ Invalid device number. Please choose from the list above.")
            except ValueError:
                print("✗ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n✗ Cancelled by user")
                sys.exit(0)

    def configure_recording(self, device):
        """Configure sample rate and channels"""
        print("\n" + "=" * 70)
        print("RECORDING CONFIGURATION")
        print("=" * 70)
        print(f"Device: {device['name']}")

        # Sample rate selection
        print("\nAvailable sample rates:")
        print("  [1] 44100 Hz (CD quality)")
        print("  [2] 48000 Hz (Professional, recommended)")
        print("  [3] 96000 Hz (High-res audio)")

        while True:
            try:
                choice = input("\nSelect sample rate [1-3, default=2]: ").strip() or "2"
                sample_rates = {1: 44100, 2: 48000, 3: 96000}
                self.samplerate = sample_rates.get(int(choice))

                if self.samplerate:
                    # Validate sample rate with device
                    try:
                        sd.check_input_settings(device=self.device, samplerate=self.samplerate)
                        print(f"✓ Sample rate: {self.samplerate} Hz")
                        break
                    except sd.PortAudioError as e:
                        print(f"⚠ Device doesn't support {self.samplerate} Hz")
                        self.samplerate = int(device['default_samplerate'])
                        print(f"  Using device default: {self.samplerate} Hz")
                        break
                else:
                    print("✗ Invalid choice. Please select 1, 2, or 3.")
            except ValueError:
                print("✗ Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\n✗ Cancelled by user")
                sys.exit(0)

        # Channels selection
        max_channels = device['max_input_channels']
        print(f"\nAvailable channels (max: {max_channels}):")
        print("  [1] Mono (1 channel)")
        if max_channels >= 2:
            print("  [2] Stereo (2 channels, recommended)")

        while True:
            try:
                default = "2" if max_channels >= 2 else "1"
                choice = input(f"\nSelect channels [1-2, default={default}]: ").strip() or default
                channels = int(choice)

                if channels == 1:
                    self.channels = 1
                    print("✓ Channels: Mono (1)")
                    break
                elif channels == 2 and max_channels >= 2:
                    self.channels = 2
                    print("✓ Channels: Stereo (2)")
                    break
                else:
                    print(f"✗ Invalid choice or unsupported by device.")
            except ValueError:
                print("✗ Invalid input. Please enter 1 or 2.")
            except KeyboardInterrupt:
                print("\n\n✗ Cancelled by user")
                sys.exit(0)

        print("\n" + "=" * 70)
        print("CONFIGURATION COMPLETE")
        print("=" * 70)
        print(f"Device:       {device['name']}")
        print(f"Sample rate:  {self.samplerate} Hz")
        print(f"Channels:     {self.channels}")
        print(f"Capture:      {self.dtype}")
        if self.output_format == 'aac':
            print(f"Output:       AAC (M4A) @ 192 kbps - iOS optimized")
        else:
            print(f"Output:       WAV 16-bit PCM")
        print("=" * 70)

    def record(self):
        """Start recording audio"""
        print("\n" + "=" * 70)
        print("RECORDING")
        print("=" * 70)
        print("Press Ctrl+C to stop recording")
        print("=" * 70)

        self.frames = []
        self.recording = True
        start_time = time.time()

        try:
            print(f"\n▶ Opening audio stream...")
            print(f"  Device: {self.device}")
            print(f"  Sample rate: {self.samplerate} Hz")
            print(f"  Channels: {self.channels}")
            print(f"  Data type: {self.dtype}")

            with sd.InputStream(
                samplerate=self.samplerate,
                device=self.device,
                channels=self.channels,
                dtype=self.dtype,
                callback=self.callback
            ):
                print(f"✓ Recording started at {datetime.now().strftime('%H:%M:%S')}")
                print("\n🔴 RECORDING... (Ctrl+C to stop)\n")

                # Keep recording and show progress
                last_update = 0
                while self.recording:
                    time.sleep(0.5)
                    elapsed = time.time() - start_time

                    # Update every 2 seconds
                    if int(elapsed) > last_update and int(elapsed) % 2 == 0:
                        last_update = int(elapsed)
                        minutes = int(elapsed // 60)
                        seconds = int(elapsed % 60)
                        frame_count = len(self.frames)
                        print(f"⏱  {minutes:02d}:{seconds:02d} - {frame_count} frames recorded", end='\r')
                        sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n\n⏹  Recording stopped by user")
        except Exception as e:
            print(f"\n\n✗ Recording error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.recording = False

        elapsed = time.time() - start_time
        print(f"\n\n✓ Recording completed")
        print(f"  Duration: {elapsed:.2f} seconds")
        print(f"  Frames captured: {len(self.frames)}")

        return True

    def save_recording(self, output_path=None):
        """Save the recorded audio to a file"""
        if not self.frames:
            print("✗ No audio frames to save!")
            return False

        print("\n" + "=" * 70)
        print("SAVING RECORDING")
        print("=" * 70)

        try:
            # Concatenate frames
            print("Processing audio data...")
            audio = np.concatenate(self.frames, axis=0)
            duration = len(audio) / self.samplerate
            print(f"✓ Audio data: {audio.shape}, duration: {duration:.2f}s")

            # Generate filename if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = '.m4a' if self.output_format == 'aac' else '.wav'
                output_path = f"recording_{timestamp}{ext}"

            # Determine output format based on extension or setting
            if output_path.lower().endswith('.m4a') or output_path.lower().endswith('.aac'):
                return self._save_as_aac(audio, output_path, duration)
            else:
                # Ensure .wav extension
                if not output_path.lower().endswith('.wav'):
                    output_path += '.wav'
                return self._save_as_wav(audio, output_path, duration)

        except Exception as e:
            print(f"✗ Error saving file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_as_wav(self, audio, output_path, duration):
        """Save audio as WAV file"""
        print(f"Saving as WAV: {output_path}")

        # Convert float32 to int16 for WAV file
        if self.dtype == 'float32':
            audio_int16 = np.int16(audio * 32767)
            wavfile.write(output_path, self.samplerate, audio_int16)
        else:
            wavfile.write(output_path, self.samplerate, audio)

        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB

        print("\n" + "=" * 70)
        print("✓ FILE SAVED SUCCESSFULLY")
        print("=" * 70)
        print(f"Path:        {os.path.abspath(output_path)}")
        print(f"Duration:    {duration:.2f} seconds")
        print(f"Size:        {file_size:.2f} MB")
        print(f"Sample rate: {self.samplerate} Hz")
        print(f"Channels:    {self.channels}")
        print(f"Format:      16-bit PCM WAV")
        print("=" * 70)

        return True

    def _save_as_aac(self, audio, output_path, duration):
        """Save audio as AAC/M4A file using ffmpeg"""
        if not self.has_ffmpeg:
            print("✗ ffmpeg not available. Install it with: brew install ffmpeg")
            print("  Falling back to WAV format...")
            wav_path = output_path.rsplit('.', 1)[0] + '.wav'
            return self._save_as_wav(audio, wav_path, duration)

        print(f"Saving as AAC: {output_path}")

        # First save as temporary WAV
        temp_wav = output_path.rsplit('.', 1)[0] + '_temp.wav'
        print("Creating temporary WAV file...")

        if self.dtype == 'float32':
            audio_int16 = np.int16(audio * 32767)
            wavfile.write(temp_wav, self.samplerate, audio_int16)
        else:
            wavfile.write(temp_wav, self.samplerate, audio)

        # Convert to AAC using ffmpeg
        print("Converting to AAC with ffmpeg...")
        try:
            # Use high-quality AAC encoding (VBR quality 2, ~128-192 kbps)
            cmd = [
                'ffmpeg',
                '-i', temp_wav,
                '-c:a', 'aac',
                '-b:a', '192k',  # 192 kbps for high quality
                '-movflags', '+faststart',  # Optimize for streaming/iOS
                '-y',  # Overwrite output file
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"✗ ffmpeg error: {result.stderr}")
                return False

            # Remove temporary WAV file
            os.remove(temp_wav)

            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB

            print("\n" + "=" * 70)
            print("✓ FILE SAVED SUCCESSFULLY")
            print("=" * 70)
            print(f"Path:        {os.path.abspath(output_path)}")
            print(f"Duration:    {duration:.2f} seconds")
            print(f"Size:        {file_size:.2f} MB")
            print(f"Sample rate: {self.samplerate} Hz")
            print(f"Channels:    {self.channels}")
            print(f"Format:      AAC (M4A) @ 192 kbps")
            print(f"Optimized:   iOS/Apple devices")
            print("=" * 70)

            return True

        except subprocess.TimeoutExpired:
            print("✗ ffmpeg conversion timed out")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            return False
        except Exception as e:
            print(f"✗ Error during AAC conversion: {e}")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            return False

    def run(self):
        """Main application flow"""
        try:
            # List devices
            input_devices = self.list_devices()
            if not input_devices:
                return 1

            # Select device
            device = self.select_device(input_devices)

            # Configure recording
            self.configure_recording(device)

            # Get output filename
            print("\n")
            ext = '.m4a' if self.output_format == 'aac' else '.wav'
            default_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            output_path = input(f"Output filename [default: {default_filename}]: ").strip()
            if not output_path:
                output_path = default_filename

            # Record audio
            if not self.record():
                return 1

            # Save recording
            if not self.save_recording(output_path):
                return 1

            print("\n✓ All done!\n")
            return 0

        except KeyboardInterrupt:
            print("\n\n✗ Cancelled by user\n")
            return 1
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1

def main():
    """Entry point"""
    recorder = AudioRecorderCLI()
    sys.exit(recorder.run())

if __name__ == "__main__":
    main()

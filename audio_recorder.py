import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue
from datetime import datetime
import os
import sys

class AudioRecorder:
    def __init__(self):
        print("=" * 60)
        print("Audio Recorder Initialization")
        print("=" * 60)

        print(f"Python version: {sys.version}")
        print(f"sounddevice version: {sd.__version__}")
        print(f"numpy version: {np.__version__}")

        self.root = tk.Tk()
        self.root.title("High-Quality Audio Recorder")
        self.root.geometry("500x450")
        print("✓ Tkinter window created")

        # Fix for macOS blank window issue
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        print("✓ Window display fix applied")

        self.recording = False
        self.frames = []
        self.device = None
        self.samplerate = 48000
        self.channels = 2  # Stereo
        self.dtype = 'float32'  # Better compatibility than int24
        self.q = queue.Queue()

        # Get available input devices
        print("\nScanning for audio input devices...")
        self.device_list = sd.query_devices()
        self.input_devices = [(i, d) for i, d in enumerate(self.device_list) if d['max_input_channels'] > 0]

        print(f"✓ Found {len(self.input_devices)} input device(s):")
        for idx, device in self.input_devices:
            print(f"  [{idx}] {device['name']}")
            print(f"      Max channels: {device['max_input_channels']}")
            print(f"      Default sample rate: {device['default_samplerate']} Hz")

        self.setup_ui()
        print("\n✓ UI setup complete")
        print("=" * 60)

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Device selection
        ttk.Label(main_frame, text="Select Input Device:", font=('Arial', 10, 'bold')).pack(pady=(0, 5))

        self.device_var = tk.StringVar()
        device_names = [f"{d['name']}" for idx, d in self.input_devices]

        if device_names:
            self.device_var.set(device_names[0])

        device_menu = ttk.OptionMenu(main_frame, self.device_var,
                                      device_names[0] if device_names else "No devices found",
                                      *device_names)
        device_menu.pack(fill=tk.X, pady=(0, 10))

        # Refresh devices button
        refresh_btn = ttk.Button(main_frame, text="Refresh Devices", command=self.refresh_devices)
        refresh_btn.pack(pady=(0, 10))

        # Sample rate selection
        ttk.Label(main_frame, text="Sample Rate (Hz):", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        self.samplerate_var = tk.StringVar(value="48000")
        samplerate_menu = ttk.OptionMenu(main_frame, self.samplerate_var, "48000", "44100", "48000", "96000")
        samplerate_menu.pack(fill=tk.X, pady=(0, 10))

        # Channels selection
        ttk.Label(main_frame, text="Channels:", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        self.channels_var = tk.StringVar(value="2 (Stereo)")
        channels_menu = ttk.OptionMenu(main_frame, self.channels_var, "2 (Stereo)", "1 (Mono)", "2 (Stereo)")
        channels_menu.pack(fill=tk.X, pady=(0, 10))

        # Recording time display
        self.time_label = ttk.Label(main_frame, text="Recording Time: 00:00", font=('Arial', 10))
        self.time_label.pack(pady=(10, 5))

        # Level meter (simple)
        self.level_var = tk.DoubleVar()
        self.level_bar = ttk.Progressbar(main_frame, variable=self.level_var, maximum=100)
        self.level_bar.pack(fill=tk.X, pady=(0, 10))

        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start Recording", command=self.start_recording)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        # Status label
        self.status = ttk.Label(main_frame, text="Ready", font=('Arial', 9), foreground="green")
        self.status.pack(pady=10)

        # Info label
        info_text = "Connect your iPhone via USB or use laptop mic.\nHigher sample rates = better quality but larger files."
        info_label = ttk.Label(main_frame, text=info_text, font=('Arial', 8), foreground="gray")
        info_label.pack(pady=(10, 0))

        # Force window update (fixes macOS display issues)
        self.root.update_idletasks()
        self.root.update()

    def refresh_devices(self):
        """Refresh the list of available audio devices"""
        print("\n" + "=" * 60)
        print("Refreshing audio devices...")
        print("=" * 60)

        self.device_list = sd.query_devices()
        self.input_devices = [(i, d) for i, d in enumerate(self.device_list) if d['max_input_channels'] > 0]

        print(f"✓ Found {len(self.input_devices)} input device(s):")
        for idx, device in self.input_devices:
            print(f"  [{idx}] {device['name']}")

        device_names = [f"{d['name']}" for idx, d in self.input_devices]

        # Update dropdown
        menu = self.device_var.trace_remove
        self.device_var.set(device_names[0] if device_names else "No devices found")

        print("=" * 60)
        messagebox.showinfo("Devices Refreshed", f"Found {len(device_names)} input device(s)")

    def callback(self, indata, frames, time, status):
        """Audio input callback"""
        if status:
            print(f"⚠ Audio callback status: {status}")

        # Calculate RMS level for display
        rms = np.sqrt(np.mean(indata**2))
        level = min(100, rms * 100 * 10)  # Scale for display
        self.level_var.set(level)

        self.q.put(indata.copy())

    def update_recording_time(self):
        """Update recording time display"""
        if self.recording:
            elapsed = len(self.frames) * 1024 / self.samplerate  # Approximate
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_label.config(text=f"Recording Time: {minutes:02d}:{seconds:02d}")
            self.root.after(100, self.update_recording_time)

    def recording_thread(self):
        """Thread for handling audio recording"""
        print("\n▶ Recording thread started")
        try:
            print(f"  Opening audio stream:")
            print(f"    Device: {self.device}")
            print(f"    Sample rate: {self.samplerate} Hz")
            print(f"    Channels: {self.channels}")
            print(f"    Data type: {self.dtype}")
            print(f"    Block size: 1024")

            with sd.InputStream(
                samplerate=self.samplerate,
                device=self.device,
                channels=self.channels,
                dtype=self.dtype,
                callback=self.callback,
                blocksize=1024
            ):
                print("✓ Audio stream opened successfully")
                frame_count = 0
                while self.recording:
                    self.frames.append(self.q.get())
                    frame_count += 1
                    if frame_count % 100 == 0:  # Log every 100 frames (~2 seconds)
                        print(f"  Recorded {frame_count} frames ({len(self.frames) * 1024 / self.samplerate:.1f}s)")

                print(f"✓ Recording stopped. Total frames: {frame_count}")
        except Exception as e:
            print(f"✗ Recording thread error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.recording = False
            self.root.after(0, lambda: messagebox.showerror("Recording Error", f"Error: {str(e)}\n\nTry a different device or sample rate."))
            self.root.after(0, self.stop_recording)

    def start_recording(self):
        """Start audio recording"""
        print("\n" + "=" * 60)
        print("START RECORDING")
        print("=" * 60)

        device_name = self.device_var.get()
        print(f"Selected device: {device_name}")

        if not device_name or device_name == "No devices found":
            print("✗ No device selected")
            messagebox.showwarning("Warning", "Please select an input device.")
            return

        # Find device index
        self.device = next((idx for idx, d in self.input_devices if d['name'] == device_name), None)

        if self.device is None:
            print("✗ Device not found in available devices list")
            messagebox.showerror("Error", "Selected device not found. Try refreshing devices.")
            return

        print(f"✓ Device index: {self.device}")

        # Get device info and validate sample rate
        try:
            device_info = sd.query_devices(self.device, 'input')
            print(f"Device info:")
            print(f"  Name: {device_info['name']}")
            print(f"  Max input channels: {device_info['max_input_channels']}")
            print(f"  Default sample rate: {device_info['default_samplerate']} Hz")

            requested_rate = int(self.samplerate_var.get())
            print(f"Requested sample rate: {requested_rate} Hz")

            # Try to use requested sample rate, fall back to device default if needed
            try:
                sd.check_input_settings(device=self.device, samplerate=requested_rate)
                self.samplerate = requested_rate
                print(f"✓ Sample rate validated: {self.samplerate} Hz")
            except sd.PortAudioError as e:
                print(f"⚠ Sample rate {requested_rate} Hz not supported: {e}")
                self.samplerate = int(device_info['default_samplerate'])
                print(f"  Falling back to device default: {self.samplerate} Hz")
                messagebox.showinfo("Sample Rate Adjusted",
                                  f"Device doesn't support {requested_rate} Hz.\nUsing {self.samplerate} Hz instead.")

            # Set channels
            channels_text = self.channels_var.get()
            self.channels = 1 if "Mono" in channels_text else 2
            print(f"Requested channels: {self.channels}")

            # Ensure device supports the number of channels
            max_channels = device_info['max_input_channels']
            if self.channels > max_channels:
                print(f"⚠ Device supports max {max_channels} channel(s), adjusting")
                self.channels = max_channels
                messagebox.showinfo("Channels Adjusted",
                                  f"Device supports max {max_channels} channel(s).\nAdjusting accordingly.")
            else:
                print(f"✓ Channels validated: {self.channels}")

        except Exception as e:
            print(f"✗ Error querying device: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error querying device: {str(e)}")
            return

        # Initialize recording
        print("\nInitializing recording...")
        self.q = queue.Queue()
        self.frames = []
        self.recording = True
        self.start_time = datetime.now()
        print(f"✓ Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Start recording thread
        self.thread = threading.Thread(target=self.recording_thread, daemon=True)
        self.thread.start()
        print("✓ Recording thread launched")

        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status.config(text="Recording...", foreground="red")
        print("✓ UI updated")

        # Start time update
        self.update_recording_time()
        print("=" * 60)

    def stop_recording(self):
        """Stop recording and save file"""
        print("\n" + "=" * 60)
        print("STOP RECORDING")
        print("=" * 60)

        if not self.recording:
            print("⚠ Not currently recording, ignoring stop request")
            return

        self.recording = False
        print("✓ Recording flag set to False")

        # Update UI
        self.status.config(text="Stopping recording...", foreground="orange")
        self.root.update()

        # Wait for thread to finish
        print("Waiting for recording thread to finish...")
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                print("⚠ Thread did not finish within timeout")
            else:
                print("✓ Recording thread finished")

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.level_var.set(0)

        if not self.frames:
            print("✗ No audio frames captured")
            messagebox.showwarning("Warning", "No audio was recorded.")
            self.status.config(text="Ready", foreground="green")
            return

        print(f"✓ Captured {len(self.frames)} frames")
        self.status.config(text="Processing audio...", foreground="orange")
        self.root.update()

        try:
            # Concatenate frames
            print("Processing audio data...")
            audio = np.concatenate(self.frames, axis=0)
            duration = len(audio) / self.samplerate
            print(f"✓ Audio concatenated: {audio.shape}, duration: {duration:.2f}s")

            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"recording_{timestamp}.wav"
            print(f"Default filename: {default_filename}")

            # Save file dialog
            print("Opening save dialog...")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                initialfile=default_filename
            )

            if file_path:
                print(f"Saving to: {file_path}")

                # Convert float32 to int16 for better compatibility
                if self.dtype == 'float32':
                    print("Converting float32 to int16...")
                    audio_int16 = np.int16(audio * 32767)
                    wavfile.write(file_path, self.samplerate, audio_int16)
                else:
                    wavfile.write(file_path, self.samplerate, audio)

                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"✓ File saved successfully")
                print(f"  Path: {file_path}")
                print(f"  Duration: {duration:.2f} seconds")
                print(f"  Size: {file_size:.2f} MB")
                print(f"  Sample rate: {self.samplerate} Hz")
                print(f"  Channels: {self.channels}")

                messagebox.showinfo("Success",
                    f"Audio saved successfully!\n\n"
                    f"File: {os.path.basename(file_path)}\n"
                    f"Duration: {duration:.1f} seconds\n"
                    f"Size: {file_size:.2f} MB\n"
                    f"Sample Rate: {self.samplerate} Hz\n"
                    f"Channels: {self.channels}")
                self.status.config(text="Ready", foreground="green")
            else:
                print("⚠ Save cancelled by user")
                messagebox.showwarning("Warning", "Save cancelled. Recording discarded.")
                self.status.config(text="Ready", foreground="green")

        except Exception as e:
            print(f"✗ Error saving file: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error saving file: {str(e)}")
            self.status.config(text="Error - Ready", foreground="red")

        # Reset time display
        self.time_label.config(text="Recording Time: 00:00")
        print("=" * 60)

    def run(self):
        """Start the application"""
        print("\n" + "=" * 60)
        print("Application ready - entering main loop")
        print("=" * 60)
        self.root.mainloop()
        print("\n" + "=" * 60)
        print("Application closed")
        print("=" * 60)

if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("HIGH-QUALITY AUDIO RECORDER")
        print("=" * 60)
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        recorder = AudioRecorder()
        recorder.run()
    except Exception as e:
        print("\n" + "=" * 60)
        print("FATAL ERROR")
        print("=" * 60)
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)

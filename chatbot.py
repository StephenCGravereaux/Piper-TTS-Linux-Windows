#!/usr/bin/env python3
"""
Minimal Ollama + Piper-TTS Chatbot
Simple local chatbot using Ollama for LLM and Piper-TTS for voice output.

Usage:
    python chatbot.py                    # Use default settings
    python chatbot.py --voice high       # Use high quality voice
    python chatbot.py --model llama3.2   # Use different model
"""

import os
import sys
import subprocess
import tempfile
import json
import time
import requests
import platform
from pathlib import Path


# Voice model download URLs (from Piper GitHub releases)
VOICE_URLS = {
    "en_US-lessac-medium.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    "en_US-lessac-medium.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    "en_US-lessac-high.onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx",
    "en_US-lessac-high.onnx.json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx.json",
}


class OllamaPiperChatbot:
    def __init__(self, model_name="llama3.2", voice_model=None, ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.voice_model = voice_model or str(Path(__file__).parent / "voices" / "en_US-lessac-medium.onnx")
        self.ollama_url = ollama_url
        self.conversation_history = []
        self.piper_cmd = self._find_piper()

        print(f"🤖 Initializing Chatbot...")
        print(f"🦙 Model: {self.model_name}")
        print(f"🔊 Voice: {Path(self.voice_model).name}")

        self._check_ollama()
        self._ensure_model()
        self._check_piper()
        self._ensure_voice_model()

        print("✅ Ready!\n")

    def _check_ollama(self):
        """Check if Ollama is running, start it if not."""
        # First, check if already running
        if self._is_ollama_running():
            print("✅ Ollama is running")
            return

        # Try to start Ollama
        print("🔄 Ollama not running, attempting to start...")
        if not self._start_ollama():
            print("❌ Failed to start Ollama!")
            print("   Please install Ollama from: https://ollama.com/download")
            sys.exit(1)

    def _is_ollama_running(self):
        """Check if Ollama server is responding."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _start_ollama(self):
        """Attempt to start Ollama server."""
        try:
            # Check if ollama command exists
            if platform.system() == "Windows":
                # On Windows, try to find ollama in common locations
                ollama_paths = [
                    "ollama",  # In PATH
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
                    os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
                ]
                ollama_cmd = None
                for path in ollama_paths:
                    try:
                        subprocess.run([path, "--version"], capture_output=True, timeout=5)
                        ollama_cmd = path
                        break
                    except:
                        continue

                if not ollama_cmd:
                    return False

                # Start ollama serve in background (detached process on Windows)
                subprocess.Popen(
                    [ollama_cmd, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
            else:
                # On Unix-like systems
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

            # Wait for Ollama to start (up to 30 seconds)
            print("   Waiting for Ollama to start...", end="", flush=True)
            for i in range(30):
                time.sleep(1)
                print(".", end="", flush=True)
                if self._is_ollama_running():
                    print(" Started!")
                    print("✅ Ollama is running")
                    return True

            print(" Timeout!")
            return False

        except Exception as e:
            print(f"   Error starting Ollama: {e}")
            return False

    def _ensure_model(self):
        """Check if model exists, pull if needed."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            models = [m["name"] for m in response.json().get("models", [])]

            # Check for exact match
            if self.model_name in models:
                print(f"✅ Model '{self.model_name}' ready")
                return

            # Check if model without tag exists as :latest
            model_base = self.model_name.split(":")[0]
            if f"{model_base}:latest" in models and ":" not in self.model_name:
                self.model_name = f"{model_base}:latest"
                print(f"✅ Model '{self.model_name}' ready")
                return

            print(f"📥 Pulling '{self.model_name}'... (this may take a few minutes)")
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model_name},
                stream=True,
                timeout=600  # 10 minute timeout for large models
            )

            last_status = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")

                    # Only print status changes (not progress updates)
                    if status and status != last_status and "%" not in status:
                        print(f"   {status}")
                        last_status = status

                    # Show download progress on same line
                    if "completed" in data and "total" in data:
                        completed = data["completed"]
                        total = data["total"]
                        if total > 0:
                            pct = (completed / total) * 100
                            print(f"\r   Downloading: {pct:.1f}%", end="", flush=True)

            print()  # New line after progress
            print(f"✅ Model ready")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def _find_piper(self):
        """Find the piper executable."""
        # Check in venv Scripts folder first (Windows)
        venv_piper = Path(__file__).parent / "venv" / "Scripts" / "piper.exe"
        if venv_piper.exists():
            return str(venv_piper)

        # Check in venv bin folder (Linux/Mac)
        venv_piper_unix = Path(__file__).parent / "venv" / "bin" / "piper"
        if venv_piper_unix.exists():
            return str(venv_piper_unix)

        # Check in same directory as python executable
        python_dir = Path(sys.executable).parent
        piper_in_python = python_dir / ("piper.exe" if platform.system() == "Windows" else "piper")
        if piper_in_python.exists():
            return str(piper_in_python)

        # Fall back to PATH
        return "piper"

    def _check_piper(self):
        """Check if Piper is installed."""
        try:
            subprocess.run([self.piper_cmd, "--help"], capture_output=True, timeout=5)
            print("✅ Piper TTS installed")
        except:
            print("❌ Piper not found! Install with: pip install piper-tts")
            sys.exit(1)

    def _ensure_voice_model(self):
        """Download voice model if not present."""
        voice_path = Path(self.voice_model)
        json_path = Path(str(self.voice_model) + ".json")

        # Create voices directory if needed
        voices_dir = voice_path.parent
        voices_dir.mkdir(parents=True, exist_ok=True)

        # Download voice model if missing
        if not voice_path.exists():
            voice_name = voice_path.name
            if voice_name in VOICE_URLS:
                print(f"📥 Downloading voice model '{voice_name}'...")
                try:
                    response = requests.get(VOICE_URLS[voice_name], stream=True)
                    response.raise_for_status()
                    total = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    with open(voice_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                pct = (downloaded / total) * 100
                                print(f"\r   Downloading: {pct:.1f}%", end="", flush=True)
                    print(f"\n✅ Voice model downloaded")
                except Exception as e:
                    print(f"\n❌ Failed to download voice: {e}")
                    sys.exit(1)
            else:
                print(f"❌ Voice model not found: {voice_path}")
                sys.exit(1)

        # Download JSON config if missing
        if not json_path.exists():
            json_name = json_path.name
            if json_name in VOICE_URLS:
                print(f"📥 Downloading voice config '{json_name}'...")
                try:
                    response = requests.get(VOICE_URLS[json_name])
                    response.raise_for_status()
                    with open(json_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Voice config downloaded")
                except Exception as e:
                    print(f"❌ Failed to download config: {e}")
                    sys.exit(1)

    def text_to_speech(self, text):
        """Convert text to speech using Piper."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_file = f.name

            print("🔊 Generating speech...", end="", flush=True)

            result = subprocess.run(
                [self.piper_cmd, "--model", self.voice_model, "--output_file", audio_file],
                input=text,
                text=True,
                capture_output=True,
                timeout=60
            )

            # Check if speech generation was successful
            if result.returncode != 0:
                print(" Failed!")
                print(f"⚠️  Piper error: {result.stderr}")
                return

            # Verify audio file was created and has content
            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                print(" Failed!")
                print("⚠️  No audio file generated")
                return

            print(" Done!")
            print("▶️  Playing audio...")

            self._play_audio(audio_file)

            # Clean up temp file
            try:
                os.unlink(audio_file)
            except:
                pass

        except subprocess.TimeoutExpired:
            print(" Timeout!")
            print("⚠️  Speech generation took too long")
        except Exception as e:
            print(f" Error!")
            print(f"⚠️  TTS error: {e}")

    def _play_audio(self, audio_file):
        """Play audio file."""
        system = platform.system()
        try:
            if system == "Windows":
                # Use PowerShell to play the audio synchronously
                result = subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()"],
                    timeout=60,
                    capture_output=True
                )
                if result.returncode != 0:
                    print(f"⚠️  Playback issue: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            elif system == "Darwin":
                subprocess.run(["afplay", audio_file], timeout=60)
            else:
                played = False
                for player in ["aplay", "paplay", "ffplay"]:
                    try:
                        subprocess.run([player, audio_file], timeout=60)
                        played = True
                        break
                    except FileNotFoundError:
                        continue
                if not played:
                    print("⚠️  No audio player found (tried: aplay, paplay, ffplay)")
        except subprocess.TimeoutExpired:
            print("⚠️  Audio playback timed out")
        except Exception as e:
            print(f"⚠️  Playback error: {e}")

    def chat(self, user_message, use_voice=True):
        """Send message and get response."""
        print(f"\n👤 You: {user_message}")

        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": self.conversation_history,
                    "stream": False
                },
                timeout=120
            )

            result = response.json()

            # Check for error in response
            if "error" in result:
                print(f"❌ Ollama error: {result['error']}")
                # Remove failed message from history
                self.conversation_history.pop()
                return None

            # Extract message content
            if "message" not in result:
                print(f"❌ Unexpected response format: {result}")
                self.conversation_history.pop()
                return None

            assistant_message = result["message"]["content"]

            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            print(f"🤖 Assistant: {assistant_message}")

            if use_voice:
                self.text_to_speech(assistant_message)

            return assistant_message
        except requests.exceptions.Timeout:
            print("❌ Request timed out. The model may be loading or busy.")
            self.conversation_history.pop()
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            # Remove failed message from history
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            return None

    def run_interactive(self):
        """Run interactive chat loop."""
        print("=" * 60)
        print("🎙️  OLLAMA + PIPER CHATBOT")
        print("=" * 60)
        print("Commands:")
        print("  - Type your message and press Enter")
        print("  - Type 'voice:medium' or 'voice:high' to switch voices")
        print("  - Type 'quit' or 'exit' to end")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye!")
                    break

                # Voice switching
                if user_input.lower().startswith("voice:"):
                    voice_type = user_input.split(":")[1].strip()
                    voices_dir = Path(__file__).parent / "voices"

                    if voice_type == "medium":
                        self.voice_model = str(voices_dir / "en_US-lessac-medium.onnx")
                        print(f"🔊 Switched to medium quality voice")
                    elif voice_type == "high":
                        self.voice_model = str(voices_dir / "en_US-lessac-high.onnx")
                        print(f"🔊 Switched to high quality voice")
                    else:
                        print(f"⚠️  Unknown voice: {voice_type}")
                    continue

                # Chat
                self.chat(user_input, use_voice=True)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Ollama + Piper TTS Chatbot")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name")
    parser.add_argument("--voice", choices=["medium", "high"], default="medium", help="Voice quality")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama API URL")

    args = parser.parse_args()

    # Set voice model path
    voices_dir = Path(__file__).parent / "voices"
    voice_model = str(voices_dir / f"en_US-lessac-{args.voice}.onnx")

    # Create chatbot
    chatbot = OllamaPiperChatbot(
        model_name=args.model,
        voice_model=voice_model,
        ollama_url=args.url
    )

    # Run interactive mode
    chatbot.run_interactive()


if __name__ == "__main__":
    main()


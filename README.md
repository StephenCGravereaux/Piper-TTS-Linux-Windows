# 🎙️ Minimal Ollama + Piper TTS Chatbot

A simple, standalone voice-interactive chatbot using **Ollama** for local LLM inference and **Piper TTS** for offline text-to-speech.

## 📦 What's Included

```
piper_ollama_minimal/
├── chatbot.py              # Main chatbot script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── voices/                # Piper voice models
    ├── en_US-lessac-medium.onnx
    ├── en_US-lessac-medium.onnx.json
    ├── en_US-lessac-high.onnx
    └── en_US-lessac-high.onnx.json
```

## 🚀 Quick Start

### Option A: Docker (Recommended) Note: Docker contrainers are isolated from your host's audio system. On Windows/Mac containers can't access your sound card directly. Use option B if you need to hear the voice responses.

```bash
# Pull the image
docker pull stephencgravereaux/piper-ollama-chatbot:latest

# Run interactively (Ollama must be running on host)
docker run -it --rm stephencgravereaux/piper-ollama-chatbot:latest
```

Or build locally:
```bash
docker build -t piper-ollama-chatbot .
docker run -it --rm piper-ollama-chatbot
```

> ⚠️ **Note:** Ollama must be running on your host machine. The container connects to it via `host.docker.internal:11434`.

---

### Option B: Local Python

#### 1. Install Ollama

**Windows:**
```bash
winget install Ollama.Ollama
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Start Ollama Service

```bash
ollama serve
```

Leave this running in a separate terminal.

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the Chatbot

```bash
python chatbot.py
```

## 🎯 Usage

### Basic Usage

```bash
python chatbot.py
```

### Use High Quality Voice

```bash
python chatbot.py --voice high
```

### Use Different Model

```bash
python chatbot.py --model llama3.2:3b
```

### Interactive Commands

Once running, you can:
- **Chat**: Just type your message and press Enter
- **Switch voice**: Type `voice:medium` or `voice:high`
- **Exit**: Type `quit`, `exit`, or `bye`

## 📋 Requirements

- **Python 3.8+**
- **Ollama** (running locally)
- **piper-tts** (installed via pip)
- **requests** (installed via pip)

## 🔊 Voice Models

Two voice models are included:

- **en_US-lessac-medium.onnx** - Medium quality (default)
- **en_US-lessac-high.onnx** - High quality (better sound, slower)

Switch between them during chat with `voice:medium` or `voice:high`.

## 🦙 Supported Models

Any Ollama model works! Popular choices:

- `llama3.2:1b` - Fastest, lowest memory (default)
- `llama3.2:3b` - Balanced performance
- `llama3.2` - Full model, best quality

The chatbot will automatically download the model if not already installed.

## 🛠️ Troubleshooting

### "Ollama not running!"

Make sure Ollama is running:
```bash
ollama serve
```

### "Piper not found!"

Install Piper TTS:
```bash
pip install piper-tts
```

### Audio not playing (Linux)

Install an audio player:
```bash
sudo apt install alsa-utils  # For aplay
# or
sudo apt install pulseaudio-utils  # For paplay
```

## 📝 Example Session

```
🤖 Initializing Chatbot...
🦙 Model: llama3.2:1b
🔊 Voice: en_US-lessac-medium.onnx
✅ Ollama is running
✅ Model 'llama3.2:1b' ready
✅ Piper TTS installed
✅ Ready!

============================================================
🎙️  OLLAMA + PIPER CHATBOT
============================================================
Commands:
  - Type your message and press Enter
  - Type 'voice:medium' or 'voice:high' to switch voices
  - Type 'quit' or 'exit' to end
============================================================

You: What is the capital of France?

👤 You: What is the capital of France?
🤖 Assistant: The capital of France is Paris.
[Audio plays]

You: voice:high
🔊 Switched to high quality voice

You: Tell me a fun fact
👤 You: Tell me a fun fact
🤖 Assistant: Did you know that honey never spoils? Archaeologists have found 3000-year-old honey in Egyptian tombs that was still edible!
[Audio plays]

You: quit
👋 Goodbye!
```

## 🎓 Features

- ✅ **100% Offline** - No internet required after setup
- ✅ **Privacy-First** - All processing happens locally
- ✅ **Voice Output** - Natural-sounding speech synthesis
- ✅ **Two Voice Options** - Medium and high quality
- ✅ **Conversation Memory** - Maintains chat history
- ✅ **Cross-Platform** - Works on Windows, Linux, and macOS
- ✅ **Minimal Dependencies** - Only 2 Python packages

## 📄 License

This is a minimal demonstration project. Voice models are from the Piper TTS project.

---





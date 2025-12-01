# Ollama + Piper TTS Chatbot - Usage Guide

## Quick Start

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the chatbot
python chatbot.py
```

The script will **automatically start Ollama** if it's not already running.

---

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `llama3.2` | Ollama model to use |
| `--voice` | `medium` | Voice quality (`medium` or `high`) |
| `--url` | `http://localhost:11434` | Ollama API URL |

### Examples

```bash
# Use default settings (llama3.2, medium voice)
python chatbot.py

# Use high quality voice
python chatbot.py --voice high

# Use a different model
python chatbot.py --model llama3.2
python chatbot.py --model mistral
python chatbot.py --model phi3

# Combine options
python chatbot.py --model llama3.2 --voice high
```

---

## Interactive Commands

While chatting, you can use these commands:

| Command | Action |
|---------|--------|
| `voice:medium` | Switch to medium quality voice |
| `voice:high` | Switch to high quality voice |
| `quit` / `exit` / `bye` | Exit the chatbot |

---

## Requirements

### 1. Ollama
- **Download:** https://ollama.com/download
- The script will auto-start Ollama if installed but not running
- Models are automatically downloaded on first use

### 2. Piper TTS
```bash
pip install piper-tts
```

### 3. Voice Models
Place voice files in the `voices/` directory:
- `en_US-lessac-medium.onnx` + `.json` (medium quality)
- `en_US-lessac-high.onnx` + `.json` (high quality)

Download voices from: https://github.com/rhasspy/piper/releases

---

## Troubleshooting

### "Ollama not running" / Auto-start fails
1. Ensure Ollama is installed: https://ollama.com/download
2. Try starting manually: `ollama serve`
3. Check if port 11434 is blocked

### "Piper not found"
```bash
pip install piper-tts
```

### No audio playback
- **Windows:** Uses built-in PowerShell audio
- **Mac:** Requires `afplay` (built-in)
- **Linux:** Requires `aplay`, `paplay`, or `ffplay`

### Model download slow
First-time model downloads can take several minutes depending on:
- Model size (1b models are ~1GB, larger models are bigger)
- Internet speed

---

## Project Structure

```
piper_ollama_minimal/
├── chatbot.py          # Main chatbot script
├── requirements.txt    # Python dependencies
├── USAGE.md           # This file
└── voices/            # Piper voice models
    ├── en_US-lessac-medium.onnx
    ├── en_US-lessac-medium.onnx.json
    ├── en_US-lessac-high.onnx
    └── en_US-lessac-high.onnx.json
```


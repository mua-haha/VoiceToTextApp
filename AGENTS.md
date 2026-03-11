# Voice to Text Application - AGENTS.md

## Project Overview

This is a Python-based voice-to-text application that uses:
- **Porcupine** for wake word detection (custom Chinese wake word)
- **OpenAI Whisper** for local offline speech-to-text
- **PyAudio** for microphone audio capture

## Project Structure

```
voice-to-text/
├── config.yaml              # Configuration file
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── models/                  # Wake word model files (.ppn)
├── recordings/             # Output transcriptions
└── src/
    ├── wake_word.py        # Porcupine wake word detection
    ├── audio_recorder.py   # Audio recording with silence detection
    └── stt.py             # Whisper speech-to-text
```

## Build / Run Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```

### Setup FFmpeg (Windows - Required for Whisper)
1. Download FFmpeg from https://gyty.com/soft/FFmpeg.zip
2. Extract and add to PATH, or place ffmpeg.exe in project root

### Configuration
Before running, edit `config.yaml`:
1. Set your Porcupine AccessKey (get free key from https://console.picovoice.ai/)
2. Verify keyword_paths points to your wake word model

---

## Code Style Guidelines

### General Principles
- Write clean, readable, and maintainable code
- Follow Python PEP 8 style guide
- Use type hints for function signatures
- Keep functions focused and single-purpose

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports (e.g., `from src.wake_word import WakeWordDetector`)
- Group imports by type with blank lines between groups

Example:
```python
import os
import sys
import json
from datetime import datetime

import yaml
import numpy as np

from src.wake_word import WakeWordDetector
from src.audio_recorder import AudioRecorder
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase | `wake_word.py` |
| Classes | PascalCase | `WakeWordDetector` |
| Functions | snake_case | `load_model()` |
| Variables | snake_case | `audio_data` |
| Constants | UPPER_SNAKE | `MAX_CHUNK_SIZE` |
| Private methods | _snake_case | `_validate_config()` |

### Type Hints
Always use type hints for function parameters and return values:
```python
def process_audio(audio_data: bytes, sample_rate: int = 16000) -> str:
    ...
```

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors before re-raising
- Never swallow exceptions silently

Example:
```python
def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
```

### Context Managers
Use context managers (`with` statement) for resource management:
```python
with AudioRecorder() as recorder:
    recorder.start_recording()
    # ...
# Automatically cleaned up
```

### Docstrings
Use Google-style docstrings for public functions:
```python
def transcribe(audio_data: bytes, sample_rate: int = 16000) -> str:
    """Transcribe audio data to text using Whisper.
    
    Args:
        audio_data: Raw audio bytes in PCM format.
        sample_rate: Audio sample rate in Hz (default: 16000).
        
    Returns:
        Transcribed text string.
        
    Raises:
        RuntimeError: If model is not loaded.
    """
```

### Configuration
- Store all configuration in `config.yaml`
- Never hardcode configuration values in code
- Validate required config keys at startup

### Constants
Define magic numbers as named constants:
```python
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SIZE = 1024
SILENCE_THRESHOLD_MS = 2000
```

### File Organization
1. Imports
2. Constants
3. Type definitions (if any)
4. Classes/Functions
5. Main execution block (if any)

---

## Testing Guidelines

This project does not currently have unit tests. If adding tests:
- Use `pytest` as the test framework
- Place tests in `tests/` directory
- Follow naming: `test_<module_name>.py`
- Mock external dependencies (microphone, file I/O)

---

## Common Issues

### Windows Audio Issues
If you encounter audio errors on Windows:
1. Install PyAudio wheel: `pip install pipwin && pipwin install pyaudio`
2. Or download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### FFmpeg Not Found
If Whisper can't find FFmpeg:
- Add FFmpeg to PATH, or
- Place ffmpeg.exe in project root

### Model Download
Whisper models are downloaded automatically on first use (~500MB for small model).

import whisper
import numpy as np
from typing import Optional
import io
import wave


class SpeechToText:
    def __init__(
        self,
        model_name: str = "small",
        language: str = "zh",
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.language = language
        self.device = device
        
        self._model: Optional[whisper.Whisper] = None
        
    def load_model(self) -> None:
        self._model = whisper.load_model(self.model_name, device=self.device)
        
    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        result = self._model.transcribe(
            audio_np,
            language=self.language,
            fp16=self.device != "cpu"
        )
        
        return result["text"].strip()
        
    def transcribe_from_file(self, filepath: str) -> str:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        result = self._model.transcribe(filepath, language=self.language)
        return result["text"].strip()
        
    def __enter__(self):
        self.load_model()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._model = None

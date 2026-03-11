import pvporcupine
import pyaudio
import numpy as np
from typing import Optional, Callable


class WakeWordDetector:
    def __init__(
        self,
        access_key: str,
        keyword_paths: list[str],
        sensitivity: float = 0.5,
        sample_rate: int = 16000,
        chunk_size: int = 512
    ):
        self.access_key = access_key
        self.keyword_paths = keyword_paths
        self.sensitivity = sensitivity
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        self._porcupine: Optional[pvporcupine.Porcupine] = None
        self._audio: Optional[pyaudio.PyAudio] = None
        self._stream = None
        
    def initialize(self) -> None:
        model_path = "models/porcupine_params_zh.pv"

        self._porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=self.keyword_paths,
            sensitivities=[self.sensitivity],
            model_path=model_path
        )
        
        self._audio = pyaudio.PyAudio()
        
    def start_listening(self, callback: Callable[[], None]) -> None:
        if self._porcupine is None:
            raise RuntimeError("WakeWordDetector not initialized. Call initialize() first.")
            
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._create_callback(callback)
        )
        self._stream.start_stream()
        
    def _create_callback(self, callback: Callable[[], None]):
        def inner_callback(in_data, frame_count, time_info, status):
            pcm = np.frombuffer(in_data, dtype=np.int16)
            keyword_index = self._porcupine.process(pcm)
            
            if keyword_index >= 0:
                callback()
                
            return (in_data, pyaudio.paContinue)
        return inner_callback
    
    def stop_listening(self) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
            
    def release(self) -> None:
        self.stop_listening()
        
        if self._porcupine is not None:
            self._porcupine.delete()
            self._porcupine = None
            
        if self._audio is not None:
            self._audio.terminate()
            self._audio = None
            
    def __enter__(self):
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

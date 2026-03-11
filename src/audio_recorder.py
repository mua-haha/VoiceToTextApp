import pyaudio
import numpy as np
import wave
import os
from typing import Optional
from datetime import datetime


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        silence_threshold: float = 2.0,
        min_record_duration: float = 0.5
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.min_record_duration = min_record_duration
        
        self._audio: Optional[pyaudio.PyAudio] = None
        self._stream = None
        self._frames: list[bytes] = []
        self._is_recording = False
        self._silence_count = 0
        
    def initialize(self) -> None:
        self._audio = pyaudio.PyAudio()
        
    def start_recording(self) -> None:
        if self._audio is None:
            raise RuntimeError("AudioRecorder not initialized. Call initialize() first.")
            
        self._frames = []
        self._is_recording = True
        self._silence_count = 0
        
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
    def record_chunk(self) -> bool:
        if self._stream is None:
            return False
            
        data = self._stream.read(self.chunk_size, exception_on_overflow=False)
        self._frames.append(data)
        
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        # print(f"RMS: {rms:.2f}, silence_count: {self._silence_count}")
        
        if rms < 500:
            self._silence_count += 1
        else:
            self._silence_count = 0
            
        silence_chunks = int(self.silence_threshold * self.sample_rate / self.chunk_size)
        
        if self._silence_count >= silence_chunks and len(self._frames) > self.min_record_duration * self.sample_rate / self.chunk_size:
            return False
            
        return True
        
    def stop_recording(self) -> bytes:
        self._is_recording = False
        
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
            
        audio_data = b''.join(self._frames)
        return audio_data
        
    def save_to_wav(self, filepath: str, audio_data: bytes) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self._audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
            
    def release(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
            
        if self._audio is not None:
            self._audio.terminate()
            self._audio = None
            
    def __enter__(self):
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

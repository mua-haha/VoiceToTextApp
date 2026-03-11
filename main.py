import os
import sys
import yaml
import time
import json
import threading
from datetime import datetime
from src.wake_word import WakeWordDetector
from src.audio_recorder import AudioRecorder
from src.stt import SpeechToText


class VoiceToTextApp:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._validate_config()
        self._wake_event = threading.Event()  # 使用 Event 替代布尔标志
        
    def _load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def _validate_config(self) -> None:
        porcupine_cfg = self.config.get("porcupine", {})
        if not porcupine_cfg.get("access_key"):
            raise ValueError("Porcupine access_key is required in config.yaml")
        if not porcupine_cfg.get("keyword_paths"):
            raise ValueError("Porcupine keyword_paths is required in config.yaml")
            
    def _on_wake_word_detected(self) -> None:
        print("\n" + "="*50)
        print("唤醒词已检测到！请说话...")
        print("="*50 + "\n")
        self._wake_event.set()  # 设置事件
        
    def _process_audio(self, audio_data: bytes) -> str:
        with SpeechToText(
            model_name=self.config["whisper"]["model"],
            language=self.config["whisper"]["language"],
            device=self.config["whisper"]["device"]
        ) as stt:
            text = stt.transcribe(audio_data)
            return text
            
    def _save_result(self, text: str) -> None:
        output_cfg = self.config.get("output", {})
        
        if not output_cfg.get("save_to_file", True):
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = output_cfg.get("output_dir", "recordings")
        save_format = output_cfg.get("save_format", "txt")
        
        os.makedirs(output_dir, exist_ok=True)
        
        if save_format == "txt":
            filepath = os.path.join(output_dir, f"{timestamp}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
                
        elif save_format == "json":
            filepath = os.path.join(output_dir, f"{timestamp}.json")
            data = {
                "timestamp": timestamp,
                "text": text
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        elif save_format == "markdown":
            filepath = os.path.join(output_dir, f"{timestamp}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {timestamp}\n\n{text}\n")
                
        print(f"[已保存到: {filepath}]")
        
    def _print_result(self, text: str) -> None:
        if self.config.get("output", {}).get("print_to_console", True):
            print("\n" + "="*50)
            print("转写结果:")
            print("-"*50)
            print(text)
            print("="*50 + "\n")
            
    def run(self) -> None:
        print("正在加载 Whisper 模型...")
        
        with SpeechToText(
            model_name=self.config["whisper"]["model"],
            language=self.config["whisper"]["language"],
            device=self.config["whisper"]["device"]
        ) as stt:
            print("模型加载完成！")
            print("\n" + "="*50)
            print("语音转文字程序已启动")
            print(f"请说出唤醒词开始录音...")
            print("按 Ctrl+C 退出程序")
            print("="*50 + "\n")
            
            with AudioRecorder(
                sample_rate=self.config["audio"]["sample_rate"],
                channels=self.config["audio"]["channels"],
                chunk_size=self.config["audio"]["chunk_size"],
                silence_threshold=self.config["audio"]["silence_threshold"],
                min_record_duration=self.config["audio"]["min_record_duration"]
            ) as recorder:
                
                detector = WakeWordDetector(
                    access_key=self.config["porcupine"]["access_key"],
                    keyword_paths=self.config["porcupine"]["keyword_paths"],
                    sensitivity=self.config["porcupine"]["sensitivity"],
                    sample_rate=self.config["audio"]["sample_rate"],
                    chunk_size=self.config["audio"]["chunk_size"]
                )
                detector.initialize()
                
                try:
                    while True:
                        self._wake_event.clear()  # 清除事件标志
                        
                        print("正在监听唤醒词...")
                        detector.start_listening(self._on_wake_word_detected)
                        
                        # 等待唤醒词检测
                        while not self._wake_event.is_set():
                            time.sleep(0.01)
                        
                        detector.stop_listening()
                        
                        # 开始录音
                        print("正在录音...")
                        recorder.start_recording()
                        
                        while recorder.record_chunk():
                            pass
                            
                        audio_data = recorder.stop_recording()
                        
                        if len(audio_data) > 0:
                            print("正在转写...")
                            text = stt.transcribe(audio_data)
                            
                            if text:
                                self._print_result(text)
                                self._save_result(text)
                            else:
                                print("[未识别到文字]")
                                
                        print(f"\n继续监听唤醒词...")
                        
                except KeyboardInterrupt:
                    print("\n\n程序已退出")
                finally:
                    detector.release()
                    
                    
if __name__ == "__main__":
    app = VoiceToTextApp()
    app.run()
# 语音转文字应用 - AGENTS.md

## 项目概述

这是一个基于Python的语音转文字应用，使用以下技术：
- **Porcupine** - 唤醒词检测（自定义中文唤醒词）
- **OpenAI Whisper** - 本地离线语音识别
- **PyAudio** - 麦克风音频采集

## 项目结构

```
voice-to-text/
├── config.yaml              # 配置文件
├── main.py                  # 应用入口
├── requirements.txt         # Python依赖
├── models/                  # 唤醒词模型文件(.ppn)
├── recordings/              # 转写结果输出目录
└── src/
    ├── wake_word.py         # Porcupine唤醒词检测
    ├── audio_recorder.py    # 音频录制与静音检测
    └── stt.py               # Whisper语音转文字
```

## 构建/运行命令

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
```

### 安装FFmpeg（Windows - Whisper需要）
1. 从 https://gyty.com/soft/FFmpeg.zip 下载FFmpeg
2. 解压并添加到PATH，或将ffmpeg.exe放到项目根目录

### 配置
运行前请编辑 `config.yaml`：
1. 设置你的Porcupine AccessKey（从 https://console.picovoice.ai/ 免费获取）
2. 确认keyword_paths指向你的唤醒词模型文件

---

## 代码风格指南

### 基本原则
- 编写简洁、可读、可维护的代码
- 遵循Python PEP 8风格指南
- 为函数签名使用类型提示
- 保持函数专注单一职责

### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地导入
4. 使用绝对导入（如 `from src.wake_word import WakeWordDetector`）
5. 按类型分组，组间用空行分隔

示例：
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

### 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写 | `wake_word.py` |
| 类 | PascalCase | `WakeWordDetector` |
| 函数 | snake_case | `load_model()` |
| 变量 | snake_case | `audio_data` |
| 常量 | UPPER_SNAKE | `MAX_CHUNK_SIZE` |
| 私有方法 | _snake_case | `_validate_config()` |

### 类型提示
始终为函数参数和返回值使用类型提示：
```python
def process_audio(audio_data: bytes, sample_rate: int = 16000) -> str:
    ...
```

### 错误处理
- 使用具体的异常类型
- 提供有意义的错误信息
- 记录错误后再重新抛出
- 绝不静默吞掉异常

示例：
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

### 上下文管理器
使用上下文管理器（`with`语句）进行资源管理：
```python
with AudioRecorder() as recorder:
    recorder.start_recording()
    # ...
# 自动清理
```

### 文档字符串
为公共函数使用Google风格的文档字符串：
```python
def transcribe(audio_data: bytes, sample_rate: int = 16000) -> str:
    """使用Whisper将音频数据转录为文本。
    
    Args:
        audio_data: PCM格式的原始音频字节。
        sample_rate: 音频采样率(Hz)，默认16000。
        
    Returns:
        转录的文本字符串。
        
    Raises:
        RuntimeError: 如果模型未加载。
    """
```

### 配置
- 所有配置存储在 `config.yaml`
- 永不硬编码配置值
- 启动时验证必需的配置键

### 常量
将魔数定义为命名常量：
```python
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SIZE = 1024
SILENCE_THRESHOLD_MS = 2000
```

### 文件组织
1. 导入
2. 常量
3. 类型定义（如有）
4. 类/函数
5. 主执行块（如有）

---

## 测试指南

本项目目前没有单元测试。如需添加测试：
- 使用 `pytest` 作为测试框架
- 放在 `tests/` 目录
- 命名规范：`test_<模块名>.py`
- 模拟外部依赖（麦克风、文件I/O）

---

## 常见问题

### Windows音频问题
遇到音频错误时：
1. 安装PyAudio wheel：`pip install pipwin && pipwin install pyaudio`
2. 或从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio 下载

### 找不到FFmpeg
如果Whisper找不到FFmpeg：
- 将FFmpeg添加到PATH，或
- 将ffmpeg.exe放到项目根目录

### 模型下载
Whisper模型首次使用时会自动下载（small模型约500MB）。

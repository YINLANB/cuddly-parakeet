"""
配置文件 - 马赛克去除项目
"""
import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
WEIGHTS_DIR = BASE_DIR / "weights"

# 确保目录存在
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
WEIGHTS_DIR.mkdir(exist_ok=True)

# 上传文件配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_DIMENSION = 8192  # 最大图像尺寸 (宽或高)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# 模型权重文件名
WEIGHTS = {
    "realesrgan": "RealESRGAN_x4plus.pth",
    "gfpgan": "GFPGANv1.4.pth",
    "realesr_anime": "RealESRGAN_x4plus_anime_6B.pth",
}

# 默认使用的超分辨率模型
DEFAULT_SR_MODEL = "realesr_anime"  # 使用已下载的动漫模型

# 模型下载 URL
MODEL_URLS = {
    "realesrgan": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x4plus.pth",
    "gfpgan": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
    "realesr_anime": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
}

# 处理配置
DEFAULT_SCALE = 4  # 默认放大倍数
DEFAULT_FACE_ENHANCE = True  # 默认启用人脸增强

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000

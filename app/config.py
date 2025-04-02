import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data.db')

# 文件上传配置
UPLOAD_DIR = PROJECT_ROOT / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# OCR配置
OCR_MODEL_PATH = PROJECT_ROOT / 'models' / 'ocr'

# 飞书配置
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')

# 服务器配置
HOST = '0.0.0.0'
PORT = 7860
DEBUG = bool(os.getenv('DEBUG', False))
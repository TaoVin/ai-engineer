# 路径全局变量定义
from pathlib import Path

# 项目根目录, 获取绝对路径，防止路径遍历和符号链接导致的意外
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# alembic 迁移文件存放路径
ALEMBIC_VERSION_DIR = BASE_DIR / "alembic" / "versions"


# 日志文件路径
LOG_DIR = BASE_DIR / "logs"

# 如果路径已存在则忽略，否则创建目录
LOG_DIR.mkdir(exist_ok=True)


# 上传文件目录
UPLOAD_DIR = BASE_DIR / "files"
UPLOAD_DIR.mkdir(exist_ok=True)


# 初始化脚本
SCRIPT_DIR: Path = BASE_DIR / "scripts"
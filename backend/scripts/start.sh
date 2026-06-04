#!/bin/bash
# ============================================
# 项目启动脚本
# 用法：
#   ./scripts/start.sh              # 默认 dev 环境
#   ./scripts/start.sh dev          # 开发环境
#   ./scripts/start.sh prod         # 生产环境
# ============================================

set -euo pipefail

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---------- 路径设置 ----------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# ---------- 解析环境参数 ----------
ENV="${1:-dev}"

if [ "$ENV" != "dev" ] && ["$ENV" != "prod" ]; then
    error "不支持的环境: $ENV（可选: dev / prod）"
fi

ENV_FILE=".env.${ENV}"

# ---------- 检查 .env 文件 ----------
if [ ! -f "$ENV_FILE" ]; then
    error "未找到配置文件: $ENV_FILE"
fi

# ---------- 从 .env 文件读取配置 ----------
# 用法: read_env KEY 默认值
# 从 .env 文件中提取指定 key 的值，处理空格、引号、注释
read_env() {
    local key="$1"
    local default="${2:-}"
    local value

    # 提取 key = value，去除行尾注释，去除首尾空格和引号
    value=$(grep -E "^${key}\s*=" "$ENV_FILE" \
        | head -1 \
        | sed "s/^${key}\s*=\s*//" \
        | sed 's/\s*#.*$//' \
        | sed 's/^["'\'']//' \
        | sed 's/["'\'']$//' \
        | xargs)

    # 如果为空则使用默认值
    if [ -z "$value" ]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# 读取关键配置
SERVER_HOST=$(read_env SERVER_HOST "0.0.0.0")
SERVER_PORT=$(read_env SERVER_PORT "8001")
DEBUG=$(read_env DEBUG "True")
LOGGER_LEVEL=$(read_env LOGGER_LEVEL "INFO")

# 导出环境变量，供 Python settings.py 读取
export ENVIRONMENT="$ENV"

# ---------- 激活虚拟环境 ----------
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    info "已激活虚拟环境"
else
    warn "未找到虚拟环境，使用系统 Python"
fi

# ---------- 环境检查 ----------
command -v python3 >/dev/null 2>&1 || error "未找到 python3"

# ---------- 打印配置摘要 ----------
echo ""
echo -e "${CYAN}========== 启动配置 ==========${NC}"
echo -e "  环境:     ${GREEN}${ENV}${NC}"
echo -e "  配置文件: ${GREEN}${ENV_FILE}${NC}"
echo -e "  地址:     ${GREEN}${SERVER_HOST}:${SERVER_PORT}${NC}"
echo -e "  调试模式: ${GREEN}${DEBUG}${NC}"
echo -e "  日志级别: ${GREEN}${LOGGER_LEVEL}${NC}"
echo -e "${CYAN}==============================${NC}"
echo ""

# ---------- 根据环境选择启动方式 ----------
if [ "$ENV" = "dev" ]; then
    # 开发环境：热重载 + 详细日志
    info "启动开发服务器..."
    info "API 文档: http://${SERVER_HOST}:${SERVER_PORT}/docs"
    info "按 Ctrl+C 停止服务器"
    echo ""

    uvicorn app.main:app \
        --host "$SERVER_HOST" \
        --port "$SERVER_PORT" \
        --reload \
        --reload-dir app \
        --reload-delay 0.5 \
        --log-level debug \
        --access-log

elif [ "$ENV" = "prod" ]; then
    # 生产环境：Gunicorn + Uvicorn Worker
    WORKERS=${WORKERS:-$(($(nproc) * 2 + 1))}

    command -v gunicorn >/dev/null 2>&1 || error "未安装 gunicorn，请运行 pip install gunicorn"

    info "启动生产服务器..."
    info "Worker 数量: ${WORKERS}"
    info "按 Ctrl+C 停止服务器"
    echo ""

    exec gunicorn app.main:app \
        --workers "$WORKERS" \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "${SERVER_HOST}:${SERVER_PORT}" \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
        --log-level "$LOGGER_LEVEL"
fi

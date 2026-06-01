#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DARKGRAY='\033[1;30m'
NC='\033[0m'

# 清理函数
cleanup() {
    echo -e "\n${RED}正在停止所有服务...${NC}"
    
    # 停止后端
    if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    
    # 停止 worker
    if [ -n "${WORKER_PID:-}" ] && kill -0 "$WORKER_PID" 2>/dev/null; then
        kill "$WORKER_PID" 2>/dev/null || true
        wait "$WORKER_PID" 2>/dev/null || true
    fi
    
    # 停止前端
    if [ -n "${FRONTEND_PID:-}" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        wait "$FRONTEND_PID" 2>/dev/null || true
    fi
    
    # 停止 Redis（如果是脚本启动的）
    if [ -n "${REDIS_PID:-}" ] && kill -0 "$REDIS_PID" 2>/dev/null; then
        kill "$REDIS_PID" 2>/dev/null || true
        wait "$REDIS_PID" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}  已停止${NC}"
}

trap cleanup EXIT INT TERM

# 停止端口占用进程
stop_port() {
    local port=$1
    local pids
    pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}  停止端口 $port 的进程: $pids${NC}"
        kill -9 $pids 2>/dev/null || true
    fi
}

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  AgentProject 启动脚本${NC}"
echo -e "${CYAN}========================================${NC}"

# ==== 1. 停旧进程 ====
echo -e "${RED}[1/4] 停止旧进程...${NC}"
stop_port 5173
stop_port 8000
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "celery worker" 2>/dev/null || true
echo -e "${GREEN}  完成${NC}"
sleep 1

# ==== 2. Redis ====
echo -e "${YELLOW}[2/4] Redis...${NC}"
if command -v redis-server &> /dev/null; then
    if pgrep -x "redis-server" > /dev/null; then
        echo -e "${GREEN}  已运行${NC}"
    else
        redis-server --daemonize yes
        REDIS_PID=$(pgrep -x "redis-server" | head -1)
        echo -e "${GREEN}  已启动 (PID: $REDIS_PID)${NC}"
    fi
else
    echo -e "${RED}  未找到 redis-server，请安装 Redis${NC}"
    echo -e "${DARKGRAY}  Ubuntu/Debian: sudo apt-get install redis-server${NC}"
    echo -e "${DARKGRAY}  CentOS/RHEL:  sudo yum install redis${NC}"
    echo -e "${DARKGRAY}  macOS:        brew install redis${NC}"
fi

# ==== 3. Backend & Worker ====
echo -e "${YELLOW}[3/4] Backend :8000...${NC}"
cd "$BACKEND_DIR"

# 检查虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 启动后端
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$PROJECT_ROOT/backend_server.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}  已启动 (PID: $BACKEND_PID)${NC}"

# 启动 Worker
echo -e "${YELLOW}       Worker...${NC}"
celery -A config.celery:celery_app worker --loglevel=WARNING --pool=solo > "$PROJECT_ROOT/celery_worker.log" 2>&1 &
WORKER_PID=$!
echo -e "${GREEN}  已启动 (PID: $WORKER_PID)${NC}"

# ==== 4. Frontend ====
echo -e "${YELLOW}[4/4] Frontend :5173...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  安装依赖...${NC}"
    npm install
fi

npm run dev > "$PROJECT_ROOT/frontend_server.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}  已启动 (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  前端  http://localhost:5173${NC}"
echo -e "${GREEN}  后端  http://localhost:8000${NC}"
echo -e "${DARKGRAY}  API   http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${DARKGRAY}  日志文件:${NC}"
echo -e "${DARKGRAY}    后端: $PROJECT_ROOT/backend_server.log${NC}"
echo -e "${DARKGRAY}    Worker: $PROJECT_ROOT/celery_worker.log${NC}"
echo -e "${DARKGRAY}    前端: $PROJECT_ROOT/frontend_server.log${NC}"
echo ""
echo -e "${DARKGRAY}  按 Ctrl+C 停止所有服务${NC}"
echo ""

# 等待服务就绪
echo -e "${CYAN}等待服务就绪...${NC}"
for i in {1..30}; do
    backend_ready=false
    frontend_ready=false
    
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        backend_ready=true
    fi
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        frontend_ready=true
    fi
    
    if [ "$backend_ready" = true ] && [ "$frontend_ready" = true ]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)] 前后端均已就绪！${NC}"
        break
    fi
    
    sleep 1
    
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}[警告] 服务启动超时，请检查日志${NC}"
    fi
done

# 保持运行
wait

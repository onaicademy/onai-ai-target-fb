#!/bin/bash
# AI-Таргетолог для Claude Code — автоматическая установка
# Запуск:  ./install.sh
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   AI-Таргетолог для Claude Code — установка           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo

# ─── 1. Проверки окружения ──────────────────────────────────
echo -e "${GREEN}[1/5]${NC} Проверяем зависимости..."

check_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo -e "  ${RED}✗${NC} $1 не найден. $2"
        return 1
    else
        echo -e "  ${GREEN}✓${NC} $1: $($1 --version 2>&1 | head -1)"
        return 0
    fi
}

MISSING=0
check_cmd python3 "Установи Python 3.10+ с https://python.org" || MISSING=1
check_cmd git     "Установи Git с https://git-scm.com" || MISSING=1
check_cmd npm     "Установи Node.js с https://nodejs.org" || MISSING=1

if ! command -v claude >/dev/null 2>&1; then
    echo -e "  ${YELLOW}!${NC} claude CLI не найден. Установи:  npm install -g @anthropic-ai/claude-code"
    MISSING=1
else
    echo -e "  ${GREEN}✓${NC} claude: $(claude --version 2>&1 | head -1)"
fi

if [ $MISSING -ne 0 ]; then
    echo
    echo -e "${RED}Не хватает зависимостей. Установи их и запусти заново.${NC}"
    exit 1
fi

# ─── 2. Python venv для MCP-сервера ─────────────────────────
echo
echo -e "${GREEN}[2/5]${NC} Создаём Python-окружение для MCP-сервера..."

cd "$ROOT_DIR/mcp-server"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "  ${GREEN}✓${NC} .venv создано"
else
    echo -e "  ${GREEN}✓${NC} .venv уже существует"
fi

# ─── 3. Зависимости MCP ─────────────────────────────────────
echo
echo -e "${GREEN}[3/5]${NC} Ставим зависимости MCP-сервера..."
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "  ${GREEN}✓${NC} зависимости установлены"

# ─── 4. .env ────────────────────────────────────────────────
echo
echo -e "${GREEN}[4/5]${NC} Подготавливаем файл .env..."

cd "$ROOT_DIR"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "  ${GREEN}✓${NC} .env создан из .env.example"
    NEEDS_TOKENS=1
else
    echo -e "  ${GREEN}✓${NC} .env уже существует — не трогаем"
    NEEDS_TOKENS=0
fi

# ─── 5. Готово ──────────────────────────────────────────────
echo
echo -e "${GREEN}[5/5]${NC} Проверяем структуру..."
[ -d "agent/skills" ] && echo -e "  ${GREEN}✓${NC} agent/skills/ найден"
[ -f "agent/config/AGENT.md" ] && echo -e "  ${GREEN}✓${NC} agent/config/AGENT.md найден"
[ -f "mcp-server/meta_ads_mcp/__init__.py" ] && echo -e "  ${GREEN}✓${NC} mcp-server/ инициализирован"

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  УСТАНОВКА ЗАВЕРШЕНА                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

if [ $NEEDS_TOKENS -eq 1 ]; then
    echo
    echo -e "${YELLOW}СЛЕДУЮЩИЕ ШАГИ:${NC}"
    echo
    echo "  1. Открой файл .env в редакторе:"
    echo "     ${GREEN}open .env${NC}   (на Mac)  или  ${GREEN}code .env${NC}   (VS Code)"
    echo
    echo "  2. Заполни токены — где брать описано в:"
    echo "     ${GREEN}docs/00-full-setup-guide.md${NC}"
    echo
    echo "  3. Открой Claude Code в этой папке:"
    echo "     ${GREEN}claude${NC}"
    echo
    echo "  4. Первая команда агенту:"
    echo "     ${GREEN}> Прочитай agent/config/AGENT.md и расскажи что умеешь${NC}"
    echo
fi

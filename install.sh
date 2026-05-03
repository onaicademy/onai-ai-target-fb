#!/bin/bash
# AI-Таргетолог для Claude Code — автоустановщик
# Подключает Pipeboard Remote MCP и копирует 12 скиллов в Claude Code.
# Запуск:  ./install.sh
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   AI-Таргетолог для Claude Code — установка           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo

# ─── 1. Проверки ───────────────────────────────────────────
echo -e "${GREEN}[1/3]${NC} Проверяем что Claude Code установлен..."

if ! command -v claude >/dev/null 2>&1; then
    echo -e "  ${RED}✗${NC} claude CLI не найден"
    echo
    echo "Установи Claude Code:"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo
    exit 1
fi
echo -e "  ${GREEN}✓${NC} claude: $(claude --version 2>&1 | head -1)"

# ─── 2. Подключаем Pipeboard Remote MCP ─────────────────────
echo
echo -e "${GREEN}[2/3]${NC} Подключаем Pipeboard Remote MCP..."

if claude mcp list 2>/dev/null | grep -q "meta-ads-mcp"; then
    echo -e "  ${GREEN}✓${NC} meta-ads-mcp уже подключён"
else
    claude mcp add meta-ads-mcp \
        --transport http \
        https://meta-ads.mcp.pipeboard.co/ 2>&1 | tail -5
    echo -e "  ${GREEN}✓${NC} meta-ads-mcp подключён"
fi

# ─── 3. Копируем скиллы и конфиги ───────────────────────────
echo
echo -e "${GREEN}[3/3]${NC} Копируем 12 скиллов и конфиги..."

mkdir -p ~/.claude/skills
SKILL_COUNT=0
for skill_dir in "$ROOT_DIR/agent/skills"/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        if [ ! -d "$HOME/.claude/skills/$skill_name" ]; then
            cp -R "$skill_dir" "$HOME/.claude/skills/"
            SKILL_COUNT=$((SKILL_COUNT + 1))
        fi
    fi
done

if [ $SKILL_COUNT -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} скопировано $SKILL_COUNT скиллов в ~/.claude/skills/"
else
    echo -e "  ${YELLOW}!${NC} скиллы уже на месте (ничего не перезаписывал)"
fi

WORKSPACE_DIR="$HOME/Desktop/AI-Workspace"
if [ -d "$WORKSPACE_DIR" ]; then
    if [ ! -d "$WORKSPACE_DIR/agent" ]; then
        cp -R "$ROOT_DIR/agent/config" "$WORKSPACE_DIR/agent"
        echo -e "  ${GREEN}✓${NC} конфиги скопированы в $WORKSPACE_DIR/agent/"
    else
        echo -e "  ${YELLOW}!${NC} $WORKSPACE_DIR/agent уже существует — не перезаписываю"
    fi
else
    echo -e "  ${YELLOW}!${NC} $WORKSPACE_DIR не найден"
    echo "     Создай папку AI-Workspace на рабочем столе (Урок 2),"
    echo "     потом скопируй вручную:"
    echo "     cp -R $ROOT_DIR/agent/config $WORKSPACE_DIR/agent"
fi

# ─── Готово ────────────────────────────────────────────────
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  УСТАНОВКА ЗАВЕРШЕНА                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}СЛЕДУЮЩИЕ ШАГИ:${NC}"
echo
echo "  1. Открой Claude Code в твоём AI-Workspace:"
echo "     ${GREEN}cd ~/Desktop/AI-Workspace${NC}"
echo "     ${GREEN}claude${NC}"
echo
echo "  2. Внутри Claude введи команду авторизации в Pipeboard:"
echo "     ${GREEN}/mcp${NC}"
echo "     откроется браузер → логинишься через Facebook"
echo "     Pipeboard сам цепляет твои рекламные аккаунты"
echo
echo "  3. Первая команда агенту:"
echo "     ${GREEN}> Покажи мои рекламные аккаунты${NC}"
echo
echo "  Полная инструкция: README.md"
echo

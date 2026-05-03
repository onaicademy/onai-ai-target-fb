# Быстрый старт

Запуск AI Ads Agent за 5 шагов.

---

## Шаг 1: Установи Claude Code

### Mac
```bash
brew install claude-code
```

### Windows
Скачай установщик: https://claude.ai/download

### VS Code
Установи расширение "Claude Code" из маркетплейса.

---

## Шаг 2: Подключи MCP сервер

MCP (Model Context Protocol) — это мост между Claude и Facebook API.

### Вариант A: Локальная установка (рекомендуется)

1. Склонируй репозиторий MCP:
```bash
git clone https://github.com/YOUR_USERNAME/onai-ai-target-fb-mcp.git
cd onai-ai-target-fb-mcp
```

2. Установи зависимости:
```bash
pip install uv
uv sync
```

3. Создай файл `.mcp.json` в корне проекта:
```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uv",
      "args": ["run", "--directory", "/путь/к/onai-ai-target-fb-mcp", "meta-ads-mcp"],
      "env": {
        "META_APP_ID": "твой_app_id",
        "META_APP_SECRET": "твой_app_secret",
        "META_ACCESS_TOKEN": "твой_access_token"
      }
    }
  }
}
```

4. Получи токены:
   - Создай приложение на https://developers.facebook.com
   - Добавь продукт "Marketing API"
   - Сгенерируй Access Token с правами `ads_management`, `ads_read`

### Вариант B: Pipeboard (без установки)

1. Зарегистрируйся на https://pipeboard.co
2. Получи API токен
3. В `.mcp.json`:
```json
{
  "mcpServers": {
    "meta-ads": {
      "url": "https://mcp.pipeboard.co/meta-ads-mcp",
      "headers": {
        "Authorization": "Bearer ТВОЙ_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

**Важно:** Pipeboard использует базовый meta-ads-mcp без расширений (47 vs 29 tools).

---

## Шаг 3: Скопируй skills и конфиги

1. Скопируй папку `skills/` в `.claude/skills/` твоего проекта
2. Скопируй папку `config/` в удобное место (например, `.claude/ads-agent/`)

```bash
cp -r skills/ ~/.claude/skills/
cp -r config/ ~/.claude/ads-agent/
```

Или создай симлинки:
```bash
ln -s /путь/к/onai-ai-target-fb/skills ~/.claude/skills
```

---

## Шаг 4: Добавь первый аккаунт

1. Открой `config/ad_accounts.md`
2. Заполни данные своего аккаунта:

```markdown
## Аккаунт 1: МойБизнес

- **Account ID**: act_123456789
- **Page ID**: 987654321
- **Instagram ID**: 17841XXXXXXXXX
- **Название**: МойБизнес
- **Сайт**: https://mybusiness.com
- **Бриф**: [briefs/mybusiness.md](briefs/mybusiness.md)
- **Статус**: активен
- **Валюта**: USD
- **Часовой пояс**: UTC+3 (Москва)
- **Тип конверсии**: Lead-формы
- **Заметки**: Описание бизнеса
```

3. Создай бриф `config/briefs/mybusiness.md` по шаблону `_template.md`

---

## Шаг 5: Запусти агента

Открой терминал в папке проекта и напиши:

```
/ads-agent
```

Или любой другой skill:
- `/dashboard` — статистика по всем аккаунтам
- `/ads-optimizer` — анализ и рекомендации
- `/ads-reporter` — отчёт за период

---

## Проверка работы

Если всё настроено правильно, `/dashboard` покажет:

```
📊 Dashboard: МойБизнес

Период: today
───────────────────────────
Spend: $45.20
Leads: 12
CPL: $3.77
CTR: 1.2%
CPM: $8.50
───────────────────────────
```

---

## Проблемы?

### "MCP server not found"
- Проверь путь в `.mcp.json`
- Убедись что `uv` установлен: `which uv`

### "Access token expired"
- Обнови токен в `.mcp.json`
- Для долгосрочного токена используй System User в Business Manager

### "Permission denied"
- Проверь что токен имеет доступ к рекламному аккаунту
- Аккаунт должен быть добавлен в твоё приложение

См. подробнее: [docs/troubleshooting.md](docs/troubleshooting.md)

---

## Следующие шаги

1. Заполни бриф с целевыми метриками (CPL, бюджеты)
2. Запусти `/ads-optimizer` для первого анализа
3. Изучи `knowledge/` для понимания логики оптимизации

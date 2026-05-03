# AI-Таргетолог для Claude Code

> AI-агент, который запускает рекламу в Facebook/Instagram и оптимизирует её за тебя.
> Подключаешь к своему Claude Code — и говоришь ему «запусти кампанию», «покажи отчёт», «отключи слабые объявления».

Бонус-урок к курсу [onAI.academy — Vibe coding с Claude Code](https://onai.academy).

---

## Что это даёт

- **12 готовых скиллов** для Claude Code (агент по рекламе, оптимизатор, отчёты, дашборд, креативы, таргетинг)
- **MCP-сервер** для общения с Facebook Graph API (47 инструментов)
- **Health Score** — система автоматической оценки кампаний
- **Генерация креативов** через Gemini
- Работает прямо в **VS Code + Claude Code** на твоём компьютере

После установки ты говоришь Claude:

> «Покажи дашборд за последние 7 дней по всем аккаунтам»
> «У какой кампании Health Score просел — что отключить?»
> «Создай новую кампанию для аккаунта X на конверсии в WhatsApp с бюджетом 30 USD/день»

И он сам идёт, читает данные, пишет рекомендации, выполняет действия.

---

## Что внутри репозитория

```
onai-ai-targetolog/
├── README.md                # этот файл
├── install.sh               # автоматическая установка одной командой
├── .env.example             # шаблон файла с твоими токенами
├── .gitignore
├── LICENSE
│
├── docs/                    # документация
│   ├── 00-full-setup-guide.md   # полная инструкция (14 шагов с нуля)
│   └── 02-quickstart.md          # быстрый старт (5 шагов для опытных)
│
├── agent/                   # Claude Skills + конфиги
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── skills/              # 12 скиллов
│   ├── config/              # твои аккаунты, брифы, креативы
│   ├── examples/            # примеры заполнения
│   └── docs/                # подробная документация по агенту
│
└── mcp-server/              # Python MCP-сервер для Meta Ads API
    ├── meta_ads_mcp/
    ├── requirements.txt
    ├── pyproject.toml
    ├── Dockerfile
    └── meta_ads_auth.sh
```

---

## Быстрая установка

### Что нужно перед стартом

- **macOS / Linux / Windows** (на Windows — через WSL)
- **Python 3.10+**
- **Node.js + npm** (нужны для `claude` CLI)
- **Claude Code** установлен и залогинен ([инструкция](https://docs.anthropic.com/en/docs/claude-code))
- **Facebook Business аккаунт** с активным рекламным аккаунтом
- **VS Code** (опционально — но удобнее)

### Установка одной командой

```bash
git clone https://github.com/onaicademy/onai-ai-target-fb.git
cd onai-ai-target-fb
./install.sh
```

Скрипт сам:
- проверит зависимости
- создаст Python-окружение для MCP-сервера
- установит все нужные пакеты
- скопирует `.env.example` → `.env`
- покажет следующий шаг

### Заполнить `.env`

После установки откроешь `.env` и заполнишь:

```bash
META_APP_ID=твой_facebook_app_id
META_APP_SECRET=твой_facebook_app_secret
META_ACCESS_TOKEN=твой_long_lived_access_token
GEMINI_API_KEY=ключ_gemini_для_генерации_картинок
PIPEBOARD_API_TOKEN=токен_pipeboard_если_используешь
```

**Где брать токены** — описано в [`docs/00-full-setup-guide.md`](docs/00-full-setup-guide.md).

### Запуск

```bash
# Открой Claude Code в этой папке
claude
```

И первая команда:

```
Прочитай agent/config/AGENT.md и расскажи, что ты можешь делать с моей рекламой.
```

---

## Подробные инструкции

- **Никогда не работал с Claude Code и Facebook API?** → [`docs/00-full-setup-guide.md`](docs/00-full-setup-guide.md) — 14 шагов от регистрации FB-приложения до первой запущенной кампании.
- **Уже работал с MCP / Claude Code?** → [`docs/02-quickstart.md`](docs/02-quickstart.md) — 5 шагов.
- **Подробно про скиллы агента** → [`agent/README.md`](agent/README.md)
- **Подробно про MCP-сервер и инструменты** → [`mcp-server/README.md`](mcp-server/README.md)

---

## Безопасность

- Файл `.env` **никогда** не должен попадать в git — он в `.gitignore` по умолчанию
- Токены Facebook → ротируй каждые 60 дней
- Не давай длинные access_token третьим лицам — это полный доступ к твоему Business Manager
- Перед работой с реальными деньгами протестируй на маленьком бюджете ($1–5/день)

## Что НЕ доверять агенту

- **Финальные решения** по бюджетам — всегда подтверждай вручную
- **Запуск на больших суммах** без предварительного теста
- **Настройку доменов** и интеграций (Pixel, Conversions API) — это разовые операции, делай руками
- **Работу с чужими аккаунтами** без явного брифа клиента

---

## Поддержка

- Telegram-сообщество: [@strogo_na_opuse](https://t.me/strogo_na_opuse)
- Видео-уроки: онlineAcademy → курс «Vibe coding с Claude Code» → Бонус-урок 5

---

## Лицензия

MIT — см. [LICENSE](LICENSE). Используй, форкай, переделывай. Только не выдавай за свой первоначальный продукт без атрибуции.

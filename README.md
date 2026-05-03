# AI-Таргетолог для Claude Code

> AI-агент, который запускает рекламу в Facebook/Instagram и оптимизирует её за тебя.
> 12 готовых скиллов + подключение к Meta Ads через [Pipeboard.co](https://pipeboard.co) Remote MCP.

Бонус-урок к курсу [onAI.academy — Vibe coding с Claude Code](https://onai.academy).

---

## Что это даёт

- **12 Claude Skills** — готовый агент по рекламе: оптимизатор, отчёты, дашборд, креативы, таргетинг
- **Health Score** — система автоматической оценки кампаний
- **Генерация креативов** через Gemini
- **Подключение к Meta Ads** — через Pipeboard Remote MCP (OAuth, без токенов вручную)

После установки ты говоришь Claude:

> «Покажи дашборд по моим аккаунтам за неделю»
> «У какой кампании Health Score просел — что отключить?»
> «Создай новую кампанию для аккаунта X на конверсии в WhatsApp с бюджетом 30 USD/день»

И он сам идёт, читает данные, пишет рекомендации, выполняет действия.

---

## ⚠️ Сначала проверь Facebook-инфраструктуру

> **Pipeboard подключается только к тому, что у тебя уже есть в Facebook.** Если у тебя нет Business Manager, рекламного аккаунта или не привязана Page — после OAuth увидишь пустой список.

Перед запуском `install.sh` пройди по чеклисту:

**[Чеклист в PDF](docs/facebook-setup-pdf/00-pre-flight-checklist.pdf)** или [в Markdown](docs/facebook-setup/00-pre-flight-checklist.md) — 7 пунктов: BM, страница, рекламный аккаунт, Instagram, WhatsApp, оплата.

⚠️ **Особое внимание:** при подключении оплаты обязательно поставь галочку «я плачу налоги сам в своей стране» и впиши БИН/ИНН — иначе Facebook будет удерживать +12% НДС с каждого пополнения. Подробно: [`docs/facebook-setup/06-payment-method.md`](docs/facebook-setup/06-payment-method.md).

---

## Установка за 5 минут (рекомендуемый путь)

### Что нужно перед стартом

- **Claude Code** установлен ([инструкция](https://docs.anthropic.com/en/docs/claude-code))
- **Facebook Business аккаунт** с активным рекламным кабинетом
- Папка **AI-Workspace** на рабочем столе (как в Уроке 2)

### 4 шага

#### 1. Подключи Pipeboard Remote MCP

Одна команда в терминале:

```bash
claude mcp add meta-ads-mcp \
  --transport http \
  https://meta-ads.mcp.pipeboard.co/
```

Проверь что добавилось:

```bash
claude mcp list
```

Должен показать `meta-ads-mcp` в списке.

#### 2. Скопируй наши 12 скиллов

Клонируй этот репо и запусти автоустановщик:

```bash
git clone https://github.com/onaicademy/onai-ai-target-fb.git
cd onai-ai-target-fb
./install.sh
```

Скрипт скопирует:
- `agent/skills/*` → `~/.claude/skills/` (12 скиллов доступны во всём Claude Code)
- `agent/config/` → `~/Desktop/AI-Workspace/agent/` (твои аккаунты, брифы, креативы)

#### 3. Подключи Facebook через OAuth

Открой Claude Code в твоём AI-Workspace:

```bash
cd ~/Desktop/AI-Workspace
claude
```

Внутри Claude введи:

```
/mcp
```

Откроется браузер → логинишься через Facebook → даёшь permissions → возвращаешься в терминал. Pipeboard сам цепляет твои рекламные аккаунты.

**Никакого ручного создания API токена. Никакого `.env`. OAuth делает всё.**

#### 4. Проверка

В Claude Code:

```
Покажи мои рекламные аккаунты
```

Если видишь список аккаунтов — готово, агент работает. Дальше:

```
Прочитай agent/config/AGENT.md и расскажи что умеешь
```

Агент пройдётся по 12 скиллам и расскажет на что способен.

---

## Что внутри репозитория

```
onai-ai-target-fb/
├── README.md                # этот файл
├── install.sh               # автоустановщик скиллов и конфигов
├── LICENSE
├── docs/                    # подробные гайды
│   ├── 00-full-setup-guide.md
│   └── 02-quickstart.md
│
├── agent/                   # 🌟 главное — Claude Skills и конфиги
│   ├── skills/              # 12 скиллов (копируется в ~/.claude/skills/)
│   ├── config/              # ad_accounts, briefs, creatives, knowledge
│   ├── examples/            # примеры заполнения брифов
│   └── docs/                # документация по агенту
│
└── mcp-server/              # ⚙️ ОПЦИОНАЛЬНО: self-hosted MCP-сервер
    └── ...                  # Только если не используешь Pipeboard Remote MCP
```

Главное живёт в `agent/`. Папка `mcp-server/` — для продвинутых, кто хочет хостить MCP у себя на сервере.

---

## Первые команды агенту

После установки — попробуй эти команды по порядку:

```
1.  Покажи мои рекламные аккаунты

2.  Дай Health Score за последние 7 дней по аккаунту X

3.  Какой креатив сейчас самый эффективный, какой просел

4.  Какие кампании в зоне риска — что отключить

5.  Подготовь отчёт для клиента в HTML — выручка, ROAS, топ-кампании
```

---

## Self-hosted путь (если не хочешь Pipeboard)

Если у тебя есть причины не использовать облачный Pipeboard — можешь запустить MCP-сервер у себя.

См. [`mcp-server/README.md`](mcp-server/README.md) — там полный self-hosted setup с собственным Facebook App, токенами, Python venv. Это сложнее, но даёт полный контроль.

---

## Безопасность

- **Pipeboard OAuth** — токены живут на их сервере, ты их не видишь и не теряешь
- **Скиллы и конфиги** — все настройки и данные клиентов лежат у тебя на компе в AI-Workspace
- Перед работой с реальным бюджетом — протестируй на $1–5/день

## Что НЕ доверять агенту

- **Финальные решения** по бюджетам — всегда подтверждай вручную
- **Запуск на больших суммах** без предварительного теста
- **Настройку доменов** и Pixel/Conversions API — это разовые операции, делай руками
- **Работу с чужими аккаунтами** без явного брифа клиента

---

## Поддержка

- Telegram-сообщество: [@strogo_na_opuse](https://t.me/strogo_na_opuse)
- Видео-уроки: onAI.academy → курс «Vibe coding с Claude Code» → Бонус-урок 5
- Pipeboard support: [info@pipeboard.co](mailto:info@pipeboard.co)

## Лицензия

MIT — см. [LICENSE](LICENSE).

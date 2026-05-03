# Custom Extensions for Meta Ads MCP

This document describes custom API tools added to meta-ads-mcp from agents-monorepo.

## Overview

| Module | Tools | Description |
|--------|-------|-------------|
| status_control | 6 | Pause/resume campaigns, adsets, ads |
| audiences | 2 | Lookalike audiences management |
| batch | 1 | Batch API requests (up to 50 per call) |
| capi | 1 | Conversions API (CAPI) events |
| carousel | 4 | Carousel creative creation |
| video_upload | 2 | Video upload with chunked support |
| creative_generation | 2 | Gemini image generation (4:5, 9:16) |
| **Total** | **18** | |

---

## Status Control (`status_control.py`)

Manage the status of advertising objects.

### Tools

#### `pause_campaign(campaign_id)`
Pause a campaign by setting its status to PAUSED.

#### `resume_campaign(campaign_id)`
Resume a paused campaign by setting its status to ACTIVE.

#### `pause_adset(adset_id)`
Pause an ad set by setting its status to PAUSED.

#### `resume_adset(adset_id)`
Resume a paused ad set by setting its status to ACTIVE.

#### `pause_ad(ad_id)`
Pause an ad by setting its status to PAUSED.

#### `resume_ad(ad_id)`
Resume a paused ad by setting its status to ACTIVE.

---

## Audiences (`audiences.py`)

Lookalike audience management.

### Tools

#### `create_lookalike_audience(account_id, seed_audience_id, country, ratio=0.03, name=None)`

Create a Lookalike Audience based on a seed Custom Audience.

**Parameters:**
- `account_id` - Meta Ads account ID (format: act_XXXXXXXXX)
- `seed_audience_id` - ID of the source Custom Audience
- `country` - Country code (e.g., 'US', 'KZ', 'RU')
- `ratio` - Size as percentage (0.01-0.10, default 0.03 = 3%)
- `name` - Optional custom name

**Example:**
```python
create_lookalike_audience(
    account_id="act_123456789",
    seed_audience_id="23842588888640185",
    country="US",
    ratio=0.03
)
```

#### `get_custom_audiences(account_id, limit=25)`

Get list of Custom Audiences for an ad account.

---

## Batch API (`batch.py`)

Execute multiple Graph API requests in a single call.

### Tools

#### `batch_request(access_token, requests)`

Execute up to 50 requests per call with automatic chunking and retry.

**Parameters:**
- `access_token` - Meta API access token
- `requests` - List of request objects:
  - `method` - HTTP method: "GET", "POST", "DELETE"
  - `relative_url` - API endpoint path
  - `body` - (optional) URL-encoded body for POST

**Features:**
- Auto-splits into chunks of 50
- Exponential backoff retry (5 attempts)
- 500ms delay between chunks

**Example:**
```python
batch_request(
    access_token="...",
    requests=[
        {"method": "GET", "relative_url": "act_123/campaigns?fields=id,name"},
        {"method": "GET", "relative_url": "act_123/adsets?fields=id,name"},
        {"method": "POST", "relative_url": "123456789", "body": "status=PAUSED"}
    ]
)
```

---

## Conversions API (`capi.py`)

Send conversion events to Meta Conversions API.

### Tools

#### `send_capi_event(pixel_id, event_name, ...)`

Send a conversion event with automatic PII hashing.

**Parameters:**
- `pixel_id` - Facebook Pixel ID
- `event_name` - Standard event: ViewContent, Purchase, CompleteRegistration, Lead, AddToCart, etc.
- `phone` - User's phone (will be SHA256 hashed)
- `email` - User's email (will be SHA256 hashed)
- `client_ip_address` - User's IP (improves matching)
- `client_user_agent` - User's browser agent
- `fbc` - Facebook click ID cookie (_fbc)
- `fbp` - Facebook browser ID cookie (_fbp)
- `external_id` - Your internal user ID (will be hashed)
- `event_source_url` - URL where event occurred
- `action_source` - Event origin: website, app, email, phone_call, etc.
- `custom_data` - Additional data: currency, value, content_ids
- `event_id` - Unique ID for deduplication

**Features:**
- SHA256 hashing for phone/email
- Phone normalization (handles 8XXXXXXXXXX -> 7XXXXXXXXXX)
- Auto-generated event_id (UUID)
- Retry with exponential backoff (3 attempts)

**Example:**
```python
send_capi_event(
    pixel_id="123456789",
    event_name="Purchase",
    phone="+1234567890",
    email="user@example.com",
    custom_data={"currency": "USD", "value": 99.99}
)
```

---

## Carousel Creatives (`carousel.py`)

Create carousel ad creatives for different objectives.

### Tools

#### `create_whatsapp_carousel(account_id, cards, page_id, message, client_question, ...)`

Create a WhatsApp Click-to-WhatsApp (CTWA) carousel.

**Parameters:**
- `cards` - List of cards: [{image_hash, text, link?}] (2-10 cards)
- `page_id` - Facebook Page ID
- `message` - Primary ad text
- `client_question` - Pre-filled WhatsApp message
- `instagram_id` - (optional) Instagram account ID
- `whatsapp_phone` - (optional) WhatsApp number

#### `create_instagram_carousel(account_id, cards, page_id, instagram_id, instagram_username, message, ...)`

Create an Instagram carousel for engagement/traffic.

#### `create_website_carousel(account_id, cards, page_id, message, site_url, ...)`

Create a website traffic carousel.

**Additional Parameters:**
- `site_url` - Main website URL
- `utm` - UTM parameters to append
- `call_to_action` - CTA type: LEARN_MORE, SHOP_NOW, etc.

#### `create_leadform_carousel(account_id, cards, page_id, message, lead_form_id, ...)`

Create a lead generation carousel with instant form.

**Additional Parameters:**
- `lead_form_id` - ID of the lead generation form
- `call_to_action` - CTA type: SIGN_UP, GET_QUOTE, etc.

---

## Video Upload (`video_upload.py`)

Upload videos with automatic chunked upload for large files.

### Tools

#### `upload_video(account_id, file_path, title=None)`

Upload a video to Meta Ads.

**Parameters:**
- `account_id` - Meta Ads account ID
- `file_path` - Absolute path to video file
- `title` - (optional) Video title

**Features:**
- < 50MB: Simple upload
- >= 50MB: Chunked upload (START -> TRANSFER -> FINISH)
- Supports up to 4GB files
- Retry with exponential backoff (5 attempts per chunk)
- 4MB chunk size

**Supported formats:** MP4, MOV, AVI, MKV, WEBM (recommended: MP4 with H.264)

**Example:**
```python
upload_video(
    account_id="act_123456789",
    file_path="/path/to/video.mp4",
    title="My Product Ad"
)
```

#### `get_video_status(video_id)`

Check the processing status of an uploaded video.

**Returns:**
- `status.video_status` - "ready", "processing", or "error"
- `status.processing_progress` - 0-100 percentage

---

## Creative Generation (`creative_generation.py`)

Generate advertising images via Gemini 2.0 Flash Experimental.

**Requirements:**
- `GEMINI_API_KEY` environment variable
- `pip install google-generativeai`

### Tools

#### `generate_creative_image(prompt, offer, bullets, profits, cta, reference_image_path, output_dir)`

Generate a 4:5 Instagram creative image with text overlay.

**Parameters:**
- `prompt` - Style prompt (colors, mood, objects, background)
- `offer` - Main headline (6-12 words)
- `bullets` - 3 bullet points separated by `\n`
- `profits` - Benefit/bonus text
- `cta` - Call-to-action text (default: "Узнать больше")
- `reference_image_path` - (optional) Path to reference image for style
- `output_dir` - (optional) Output directory (default: current working directory)

**Returns:**
```json
{
  "success": true,
  "file_path": "/path/to/creative_20240115_143022.png",
  "format": "4:5 (1080x1350)"
}
```

**Example:**
```python
generate_creative_image(
    prompt="Современный минималистичный дизайн, синий градиент",
    offer="Похудей на 10 кг за месяц",
    bullets="• Без диет\n• Без тренировок\n• Результат за 30 дней",
    profits="Первая консультация бесплатно",
    cta="Записаться"
)
```

#### `expand_to_stories(image_path, output_path)`

Expand a 4:5 image to 9:16 Stories format via seamless outpainting.

The original image content stays in the center while the background is extended upward and downward seamlessly.

**Parameters:**
- `image_path` - Path to the 4:5 source image
- `output_path` - (optional) Path for output (default: `{original}_stories.png`)

**Returns:**
```json
{
  "success": true,
  "file_path": "/path/to/creative_20240115_143022_stories.png",
  "format": "9:16 (1080x1920)"
}
```

**Example:**
```python
expand_to_stories(image_path="/path/to/creative_20240115_143022.png")
```

---

## Installation

These modules are automatically loaded when starting the MCP server.

For stdio transport:
```bash
uv run meta-ads-mcp
```

For HTTP transport:
```bash
uv run meta-ads-mcp --transport streamable-http --port 8080
```

## Claude Code Skills

Skills для управления рекламой через Claude Code, использующие MCP tools выше.

| Skill | Описание |
|-------|----------|
| `/ads-agent` | Точка входа — управление Facebook рекламой |
| `/ads-optimizer` | Оптимизация с 5-компонентным Health Score (-100..+100) |
| `/ads-reporter` | Multi-period отчёты (today, yesterday, 3d, 7d, 30d) |
| `/creative-analyzer` | Risk Score для креативов (0-100) |
| `/creative-copywriter` | Генерация текстов: storytelling, офферы, посты |
| `/creative-image-generator` | Генерация изображений через Gemini (4:5, 9:16) |
| `/campaign-manager` | Создание кампаний, adsets, ads |
| `/targeting-expert` | Таргетинг и аудитории |
| `/account-onboarding` | Онбординг нового аккаунта (создаёт briefs, ad_accounts) |

### Health Score (5 компонентов)

| Компонент | Вес | Описание |
|-----------|-----|----------|
| CPL Gap | ±45 | Отклонение от target CPL |
| Trends | ±15 | Динамика 3d vs 7d, 7d vs 30d |
| CTR Penalty | -8 | Штраф за CTR < 1% |
| CPM Penalty | -12 | Штраф за CPM > median×1.3 |
| Freq Penalty | -10 | Штраф за Frequency > 2 |
| Today Adj | +0..+30 | Компенсация хорошего today |
| Volume Factor | ×0.6..1.0 | Коэффициент доверия по impressions |

**Классификация:**
- `very_good` (≥+25): Scale +20..+30%
- `good` (+5..+24): Hold или +10%
- `neutral` (-5..+4): Мониторинг
- `slightly_bad` (-25..-6): Reduce -20..-50%
- `bad` (≤-25): Pause или -50%

### Risk Score для креативов (0-100)

| Risk | Уровень | Действие |
|------|---------|----------|
| 0-25 | Low | Приоритет для масштабирования |
| 26-50 | Medium | Использовать с мониторингом |
| 51-75 | High | Требует оптимизации |
| 76-100 | Critical | Рекомендуется пауза |

Skills находятся в: `agents-monorepo/.claude/skills/`

### Creative Tags (Аналитика по креативам)

Система тегов для группировки объявлений по креативам без базы данных.

**Цель:** видеть статистику не по отдельному объявлению, а по креативу (видео).

**Naming Convention:** `{creative_tag}_{описание}`

```
kitchen_30-45_msk
kitchen_lookalike
kitchen_retarget_7d
```

- **creative_tag** = первая часть до `_` = идентификатор видео
- Одно видео → много ads → группируем по тегу

**Группировка:**
```
Креатив: kitchen
├── kitchen_30-45_msk      $100, 20 leads
├── kitchen_lookalike      $150, 35 leads
└── kitchen_retarget       $80, 15 leads
────────────────────────────────────────
ИТОГО:                     $330, 70 leads, CPL $4.71
```

**Конфигурация:**
- `config/naming_convention.md` — правила именования
- `config/creatives.md` — реестр креативов (тег → файл/описание)

### История действий (Action History)

Skills читают и записывают историю действий для умных решений:

**Хранение:** `.claude/ads-agent/history/YYYY-MM/YYYY-MM-DD.md`

**5 правил на основе истории:**

| Ситуация | Правило | Исключение |
|----------|---------|------------|
| Adset < 48ч | Не трогать агрессивно | CPL > 3x target |
| Вчера снижали | Не снижать снова | CPL > 3x target |
| 3 снижения за 3 дня | Пауза вместо снижения | — |
| Вчера повышали | Не снижать сегодня | CPL > 2x target |
| Today лучше | Мониторинг вместо снижения | — |

**Формат записи:**
```markdown
| # | Тип | Object ID | Name | Old | New | Причина | Статус |
|---|-----|-----------|------|-----|-----|---------|--------|
| 1 | budget_increase | 123 | AdSet | $20 | $26 | HS +35 | success |
```

---

## Source

Based on functionality from [agents-monorepo](https://github.com/your-org/agents-monorepo):
- `services/agent-brain/src/clients/facebook.ts`
- `services/agent-brain/src/clients/metaCapiClient.ts`
- `services/creative-generation-service/src/metaApi/video.ts`
- `services/creative-generation-service/src/metaApi/carouselCreative.ts`

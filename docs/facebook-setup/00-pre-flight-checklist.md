# Pre-flight checklist — что должно быть готово в Facebook

> **Прочитай это ДО запуска `install.sh`.** Pipeboard подключается только к тому что у тебя уже есть в Facebook. Если инфраструктуры нет — после OAuth ты увидишь пустой список аккаунтов.

Ниже — 7 пунктов. Прохожу сверху вниз. На каждом — короткое описание + ссылка на официальный гайд Meta + ссылка на наш короткий стартер.

---

## ✅ Чеклист

```
[ ] 1. У меня есть личный Facebook-аккаунт (с настоящим именем)
[ ] 2. У меня создан Business Manager (BM)
[ ] 3. У меня есть бизнес-страница (Page) внутри BM
[ ] 4. У меня создан рекламный аккаунт (Ad Account) внутри BM
[ ] 5. К Page привязан Instagram-аккаунт
[ ] 6. К Page привязан WhatsApp-номер (если ведёшь рекламу в WhatsApp)
[ ] 7. К рекламному аккаунту привязан способ оплаты — С ГАЛОЧКОЙ ПРО НАЛОГИ
```

Если все 7 галочек — иди обратно в `README.md` и запускай установку. Если хотя бы одна не стоит — открывай соответствующий гайд ниже.

---

## 1. Личный Facebook-аккаунт

Должен быть на твоё **настоящее имя**. Аккаунты-однодневки и фейки Facebook банит особенно агрессивно когда к ним привязана реклама.

- Если совсем нет — заведи на [facebook.com](https://facebook.com) обычным образом, **не покупай** старые аккаунты.

## 2. Business Manager (BM)

Это «контейнер» где живут твои страницы, рекламные аккаунты, пиксели, домены, доступы для команды. Без BM нельзя нормально вести рекламу.

- Создание: [`01-business-manager.md`](01-business-manager.md)
- Официально: [Meta Business Help → Create a Business Manager account](https://www.facebook.com/business/help/1710077379203657)

## 3. Бизнес-страница (Page) внутри BM

Это публичная страница твоего бизнеса в Facebook. Она нужна потому что **реклама всегда показывается ОТ ЛИЦА страницы** — не от твоего личного аккаунта.

- Создание: [`02-business-page.md`](02-business-page.md)
- Официально: [Meta Business Help → Create a Facebook Page](https://www.facebook.com/business/help/104002523024878)

## 4. Рекламный аккаунт (Ad Account) внутри BM

Это «кошелёк» для рекламы. К нему привязана оплата, в нём живут все твои кампании. **Ad Account ≠ BM** — это разные вещи. Один BM может иметь несколько Ad Accounts.

- Создание: [`03-ad-account.md`](03-ad-account.md)
- Официально: [Meta Business Help → Create a new ad account in Business Manager](https://www.facebook.com/business/help/910137316041095)

## 5. Instagram-аккаунт привязан к Page

Если хочешь чтобы реклама шла и в Facebook, и в Instagram — Instagram-аккаунт должен быть привязан к Page через BM. Без этого Instagram-плейсменты будут отключаться при создании рекламы.

- Привязка: [`04-instagram-link.md`](04-instagram-link.md)
- Официально: [Meta Business Help → Connect an Instagram account to a Page](https://www.facebook.com/business/help/377680519582516)

## 6. WhatsApp-номер привязан к Page (опционально)

**Только если ведёшь рекламу с целью «Messages» через WhatsApp.** Для обычной рекламы на сайт / лид-формы / Instagram Direct — пропусти этот пункт.

- Привязка: [`05-whatsapp-link.md`](05-whatsapp-link.md)
- Официально: [Meta Business Help → Connect a WhatsApp Business account](https://www.facebook.com/business/help/2087193751603668)

## 7. ⚠️ Способ оплаты с галочкой про налоги

**Самый частый gotcha. Если не поставишь галочку — Facebook удерживает налог из бюджета.**

- Подробно: [`06-payment-method.md`](06-payment-method.md)
- Официально: [Meta Business Help → Add a payment method](https://www.facebook.com/business/help/716180208457684)

---

## Если что-то не получается

Реальность: настройка Facebook-инфраструктуры **не входит в этот курс**. Это базовая инфраструктура которую обычно настраивают один раз и больше не трогают. Если застрял на каком-то пункте:

1. Попробуй гайд от Meta Business Help (ссылки выше) — они актуальные
2. Если интерфейс отличается — Facebook очень часто меняет UI, ищи кнопку с похожим смыслом
3. Спроси в TG-сообществе [@strogo_na_opuse](https://t.me/strogo_na_opuse)

После того как все 7 галочек поставлены — возвращайся к `README.md` и запускай `install.sh`.

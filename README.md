
# Нейропарсер

Нейропарсер — это инструмент для парсинга и анализа новостей и контента в социальных сетях для обнаружения публикаций по определённым темам. Инструмент использует машинное обучение для предоставления пользователям целевой, релевантной информации, минимизируя количество ненужных данных. Благодаря интеграции с Telegram, нейропарсер уведомляет пользователей о найденных событиях в реальном времени.

## Как это работает

Нейропарсер использует предварительно обученную модель машинного обучения для анализа контента из различных источников. Эти источники включают:

- Русскоязычные новостные сайты
- Каналы Telegram
- Социальные группы в ВК и ОК

Парсер ищет ссылки на новости и посты в этих источниках, затем загружает данные по найденным ссылкам и анализирует их на соответствие вашим предопределённым темам. Если текст релевантен, система уведомляет вас через Telegram-бота.

## Ключевые особенности

- Парсер работает с двумя типами моделей обученными русскоязычными bert, а так же с API платных больших языковых моделей.
- Интерфейс пользователей реализован в виде  telegram бота. Важно, проект хранит только  id чатов куда добавлен бот, но не пользователей в целях безопасности.
- Нейро-парсер можно развернуть для приватного использования, что позволин более гибко настроить списки источников и доступные модели для различения новостей.
- REST API интерфейс с [документацией](https://report.antijob.net/swagger-ui/)

---

## Документация и инструкции по использованию

Доступны в [readthedocs](https://neuro-parser.readthedocs.io/ru/latest/)

---

## Вклад в проект

Мы приветствуем участие сообщества. Пожалуйста, следуйте рекомендациям, изложенным в файле [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Контакты

Если у вас есть вопросы или вам нужна дополнительная помощь, свяжитесь с нами по адресу info@antijob.net.

# Neuroparser

Neuroparser is a tool for parsing and analyzing news and social media content to detect posts on specific topics. The tool uses machine learning to provide users with targeted, relevant information while minimizing the amount of unnecessary data. With integration into Telegram, Neuroparser notifies users in real-time about detected events.

## How It Works

Neuroparser utilizes a pre-trained machine learning model to analyze content from various sources. These sources include:

- Russian-language news websites
- Telegram channels
- Social groups in VK and OK

The parser searches for links to news and posts from these sources, then downloads the data from the found links and analyzes them for relevance to your predefined topics. If the text is relevant, the system notifies you through a Telegram bot.

## Key Features

- The parser works with two types of models: trained Russian-language BERT models and APIs of paid large language models.
- The user interface is implemented as a Telegram bot. Importantly, the project only stores the chat IDs where the bot is added, but not user data, for security purposes.
- Neuroparser can be deployed for private use, allowing more flexible configuration of source lists and available models for distinguishing news.
- REST API interface with [documentation](https://report.antijob.net/swagger-ui/)

---

## Documentation and Usage Instructions

Available at [readthedocs](https://neuro-parser.readthedocs.io/en/latest/)

---

## Contributing

We welcome community participation. Please follow the guidelines outlined in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## Contact

If you have any questions or need additional assistance, contact us at info@antijob.net.

---

# 🚀 Быстрый старт - Career on Autopilot

## Шаг 1: Запуск Backend

### Вариант 1: Полный backend с AI
```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите сервер
python run_backend.py
```

### Вариант 2: Если есть ошибки с OpenAI
```bash
# Запустите исправленную версию
python run_simple.py
```

### Вариант 3: Простой тестовый backend
```bash
# Минимальная версия для тестирования подключения
python run_simple.py
```

Сервер будет доступен по адресу: `http://localhost:5000`

## Шаг 2: Запуск Frontend

Откройте любой из HTML файлов в браузере:

### Основные страницы:
- `index.html` - Главная страница
- `login.html` - Вход в систему
- `register.html` - Регистрация

### Для сотрудников:
- `profile.html` - Профиль сотрудника с AI чатом
- `applications.html` - Заявки на вакансии
- `gifts.html` - Магазин наград

### Для HR:
- `hr-panel.html` - Панель HR с AI поиском кандидатов
- `hr-profile.html` - Профиль HR
- `hr-applications.html` - Управление заявками

## Шаг 3: Тестирование

1. **Откройте `test-api.html`** для тестирования API
2. **Войдите как сотрудник**: `employee@company.com`
3. **Войдите как HR**: `hr@company.com`

## 🧪 Тестирование AI чатов

### Сотрудник (profile.html):
- "Как стать senior разработчиком?"
- "Какие навыки мне нужно развить?"
- "Найди курсы по Python"

### HR (hr-panel.html):
- "Найди senior Python разработчика"
- "Ищу DevOps инженера с Kubernetes"
- "Нужен ML инженер для проекта Alpha"

### 🎨 Markdown поддержка
AI ответы теперь отображаются с красивым форматированием:
- **Заголовки** и подзаголовки
- **Списки** и нумерация
- **Таблицы** и структурированные данные
- **Выделение** важной информации

Откройте `markdown-demo.html` для демонстрации возможностей!

## 📁 Структура проекта

```
HR/
├── model.py              # Backend Flask API
├── run_backend.py        # Скрипт запуска backend
├── requirements.txt      # Python зависимости
├── api-client.js         # API клиент для frontend
├── script.js            # Основная логика frontend
├── test-api.html        # Тестовая страница API
├── index.html           # Главная страница
├── login.html           # Страница входа
├── register.html        # Страница регистрации
├── profile.html         # Профиль сотрудника
├── applications.html    # Заявки сотрудника
├── gifts.html          # Магазин наград
├── hr-panel.html       # Панель HR
├── hr-profile.html     # Профиль HR
├── hr-applications.html # Заявки HR
└── README.md           # Подробная документация
```

## 🔧 Настройка

### Изменение API URL
В файле `api-client.js` измените:
```javascript
constructor(baseURL = 'http://localhost:5000') {
```

### Добавление новых сотрудников
В файле `model.py` в классе `MockDB` добавьте новых сотрудников в словарь `self.employees`.

## 🐛 Решение проблем

1. **CORS ошибки**: Убедитесь, что backend запущен на порту 5000
2. **API не отвечает**: Проверьте, что `flask-cors` установлен
3. **AI не работает**: Проверьте API ключ в `model.py`

## 📞 Поддержка

При возникновении проблем проверьте:
1. Все зависимости установлены
2. Backend запущен на порту 5000
3. Браузер поддерживает современный JavaScript
4. Нет блокировки CORS в браузере

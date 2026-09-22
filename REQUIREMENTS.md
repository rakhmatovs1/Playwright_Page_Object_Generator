# Playwright Page Object Generator - Requirements

## 1. Цель проекта

Разработать утилиту на Python, которая автоматически преобразует HTML-код или HTML-файлы в готовые Python Page Object классы для Playwright с интеллектуально выбранными, стабильными и поддерживаемыми локаторами.

**Основной результат**: Пользователь передаёт HTML → программа генерирует готовый Python код Page Object с правильными Playwright локаторами.

---

## 2. Что принимает генератор

### Входные данные

Генератор принимает HTML двумя способами:

#### A) HTML-строка (через API)
```python
generator = PageObjectGenerator()
po_code = generator.generate(
    html='<button>Login</button><input type="email">',
    class_name='LoginPage'
)
```

#### B) HTML-файл (через API или CLI)
```python
po_code = generator.generate_from_file(
    filepath='login.html',
    class_name='LoginPage'
)
```

#### C) Командная строка (CLI)
```bash
python main.py --input login.html --output login_page.py --class-name LoginPage
```

### Входные параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `html` или `filepath` | str | ✅ | HTML-контент или путь к файлу |
| `class_name` | str | ✅ | Имя генерируемого класса (PascalCase) |
| `output` | str | ❌ | Путь для сохранения результата (CLI only) |

---

## 3. Какие HTML элементы поддерживает

### Полностью поддерживаемые элементы

✅ **Базовые элементы:**
- `<button>` — кнопки
- `<input>` — текстовые поля, email, password, checkbox, radio
- `<textarea>` — многострочные текстовые поля
- `<select>` — выпадающие списки
- `<label>` — метки для форм
- `<form>` — контейнеры форм
- `<a>` — ссылки
- `<h1>`, `<h2>`, ..., `<h6>` — заголовки

✅ **Контейнеры:**
- `<div>` — универсальные контейнеры
- `<section>` — семантические секции
- `<nav>` — навигация
- `<header>`, `<footer>`, `<main>` — структурные элементы
- `<article>` — статьи

✅ **Таблицы:**
- `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`, `<th>` — таблицы и их части

✅ **Списки:**
- `<ul>`, `<ol>`, `<li>` — списки

✅ **Формы (продвинутые):**
- `<fieldset>` — группировка полей
- `<datalist>` — список предложений для input
- Элементы с `aria-label`, `aria-labelledby`

### Частично поддерживаемые элементы

⚠️ **Игнорируются полностью (содержимое пропускается):**
- `<script>` — скрипты
- `<style>` — стили
- `<meta>` — метаданные
- `<!-- комментарии -->` — комментарии HTML
- `<noscript>` — резервный контент
- Содержимое внутри `<head>`

⚠️ **Обрабатываются, но не создают элементы:**
- `<br>` — переносы строк
- `<hr>` — горизонтальные разделители
- `<img>` — изображения (могут иметь alt-text для локатора)

### Не поддерживаемые элементы

❌ **Не обрабатываются:**
- Собственные веб-компоненты (`<my-component>`)
- Динамически создаваемые элементы (их нельзя парсить статически)
- Shadow DOM элементы

---

## 4. Какие locator'ы умеет генерировать

### Поддерживаемые методы Playwright

Генератор может создавать следующие типы локаторов:

1. **`get_by_role()`** — по ARIA role
   ```python
   page.get_by_role("button", name="Login")
   page.get_by_role("textbox", name="Email")
   ```

2. **`get_by_label()`** — по связанному label
   ```python
   page.get_by_label("Password")
   page.get_by_label("Remember me")
   ```

3. **`get_by_placeholder()`** — по placeholder атрибуту
   ```python
   page.get_by_placeholder("Enter email")
   page.get_by_placeholder("Search...")
   ```

4. **`get_by_text()`** — по видимому тексту
   ```python
   page.get_by_text("Submit", exact=True)
   page.get_by_text("Cancel")
   ```

5. **`locator()`** с CSS селектором — по CSS пути
   ```python
   page.locator("#loginForm")
   page.locator(".submit-button")
   page.locator("input[type='email']")
   ```

6. **`locator()`** с XPath — XPath как последний fallback
   ```python
   page.locator("//button[contains(text(), 'Login')]")
   ```

---

## 5. Правила выбора locator

### Приоритетная стратегия (в порядке убывания)

Для каждого элемента генератор выбирает локатор по следующему приоритету:

#### Шаг 1: Проверка semantic role
**Условие**: Элемент имеет семантический role (button, link, textbox и т.д.)  
**Действие**: Использовать `get_by_role()`
```html
<button>Login</button>
→ page.get_by_role("button", name="Login")

<a href="/home">Home</a>
→ page.get_by_role("link", name="Home")
```

#### Шаг 2: Проверка aria-label или aria-labelledby
**Условие**: Элемент имеет `aria-label` или `aria-labelledby`  
**Действие**: Использовать `get_by_label()`
```html
<div aria-label="Close dialog">✕</div>
→ page.get_by_label("Close dialog")
```

#### Шаг 3: Проверка связанного label (for/id)
**Условие**: Это input, имеется `<label for="id">` связанная с ним  
**Действие**: Использовать `get_by_label()`
```html
<label for="email">Email</label>
<input id="email" type="email">
→ page.get_by_label("Email")
```

#### Шаг 4: Проверка placeholder
**Условие**: Input имеет `placeholder` атрибут  
**Действие**: Использовать `get_by_placeholder()`
```html
<input type="email" placeholder="Enter email">
→ page.get_by_placeholder("Enter email")
```

#### Шаг 5: Проверка видимого текста
**Условие**: Элемент имеет непустой, значимый текст внутри  
**Действие**: Использовать `get_by_text()`
```html
<button>Click me</button>
→ page.get_by_text("Click me", exact=True)

<span>Error message</span>
→ page.get_by_text("Error message")
```

#### Шаг 6: Проверка стабильных атрибутов
**Условие**: Элемент имеет `id` ИЛИ `data-testid`  
**Действие**: Использовать `locator()` с CSS
```html
<input id="password">
→ page.locator("#password")

<button data-testid="submit-btn">Submit</button>
→ page.locator("[data-testid='submit-btn']")
```

#### Шаг 7: Fallback на CSS селектор
**Условие**: Элемент имеет class или другие устойчивые селекторы  
**Действие**: Использовать `locator()` с CSS
```html
<button class="btn btn-primary">Login</button>
→ page.locator("button.btn.btn-primary")
```

#### Шаг 8: XPath (последний вариант)
**Условие**: Нет других вариантов  
**Действие**: Использовать `locator()` с XPath
```html
→ page.locator("//button[position()=1]")
```

### Специальные правила

**Исключения из приоритета:**
- **Скрытые элементы** (`display: none`, `visibility: hidden`, `hidden` атрибут) → ПРОПУСКАЮТСЯ, не создается свойство
- **Отключённые элементы** (`disabled` атрибут) → создается с комментарием `# disabled`
- **Дублирующиеся локаторы** → к имени свойства добавляется индекс (`button_1`, `button_2`)

---

## 6. Правила именования элементов

### Формат имён свойств

**Базовый формат**: `{description}_{element_type}`

**Правила:**
- ✅ **snake_case** (Python конвенция)
- ✅ Только буквы, цифры и подчеркивания
- ✅ Начинается с буквы или подчеркивания
- ❌ Не может начинаться с цифры
- ❌ Не может содержать пробелы или спецсимволы

### Примеры именования

#### По type атрибуту
```html
<input type="email" placeholder="Email">
→ email_input

<input type="password" placeholder="Password">
→ password_input

<input type="checkbox" aria-label="Remember me">
→ remember_me_checkbox
```

#### По роли элемента
```html
<button>Login</button>
→ login_button

<a href="/profile">Profile</a>
→ profile_link

<h1>Welcome</h1>
→ welcome_heading
```

#### По aria-label или label
```html
<label for="phone">Phone number</label>
<input id="phone" type="tel">
→ phone_number_input

<div aria-label="Close modal">✕</div>
→ close_modal_button
```

#### По контексту (parent элемент)
```html
<form id="loginForm">
    <input type="email">
    ...
</form>
→ login_form

<div class="search-block">
    <input type="text" placeholder="Search">
</div>
→ search_block (если это container)
```

### Обработка конфликтов

#### Случай 1: Несколько элементов одного типа
```html
<button>Login</button>
<button>Register</button>
<button>Forgot Password</button>
```
**Выход:**
```python
self.login_button = page.get_by_role("button", name="Login")
self.register_button = page.get_by_role("button", name="Register")
self.forgot_password_button = page.get_by_role("button", name="Forgot Password")
```

#### Случай 2: Идентичные элементы (без текста/label)
```html
<button></button>
<button></button>
```
**Выход:**
```python
self.button_1 = page.locator("button").nth(0)  # with warning
self.button_2 = page.locator("button").nth(1)  # with warning
```

#### Случай 3: Спецсимволы в тексте
```html
<button>Sign-Up & Continue</button>
```
**Выход:**
```python
self.sign_up_and_continue_button = page.get_by_role("button", name="Sign-Up & Continue")
```

---

## 7. Как выглядит генерируемый Page Object

### Минимальный пример

**Вход (HTML):**
```html
<button>Login</button>
<input type="email" placeholder="Email">
```

**Выход (Python):**
```python
class LoginPage:
    """Page Object for Login page."""
    
    def __init__(self, page):
        """Initialize LoginPage with Playwright page instance."""
        self.page = page
        self.login_button = page.get_by_role("button", name="Login")
        self.email_input = page.get_by_placeholder("Email")
```

### Полный пример

**Вход (HTML):**
```html
<form id="loginForm" class="auth-form">
    <h1>Sign In</h1>
    
    <label for="email">Email Address</label>
    <input id="email" type="email" required>
    
    <label for="password">Password</label>
    <input id="password" type="password" required>
    
    <input type="checkbox" id="remember" aria-label="Remember me">
    <label for="remember">Remember me</label>
    
    <button type="submit">Sign In</button>
    <button type="reset" aria-label="Clear form">Clear</button>
    
    <a href="/forgot-password">Forgot password?</a>
</form>

<div class="error-message" role="alert"></div>
```

**Выход (Python):**
```python
class LoginPage:
    """Page Object for login authentication page."""
    
    def __init__(self, page):
        """Initialize LoginPage with Playwright page instance.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        
        # Form container
        self.login_form = page.locator("#loginForm")
        
        # Header
        self.sign_in_heading = page.get_by_role("heading", level=1, name="Sign In")
        
        # Form inputs
        self.email_input = page.get_by_label("Email Address")
        self.password_input = page.get_by_label("Password")
        self.remember_me_checkbox = page.get_by_label("Remember me")
        
        # Buttons
        self.sign_in_button = page.get_by_role("button", name="Sign In")
        self.clear_button = page.get_by_label("Clear form")
        
        # Links
        self.forgot_password_link = page.get_by_role("link", name="Forgot password?")
        
        # Messages
        self.error_message = page.get_by_role("alert")
```

### Структура генерируемого кода

**Обязательные элементы:**
1. Docstring класса (кратко объясняет, для какой страницы)
2. Метод `__init__(self, page)` с параметром page (Playwright Page)
3. Присваивание `self.page = page`
4. Свойства для каждого найденного элемента

**Опциональные элементы:**
- Docstring для `__init__` метода (описание параметров)
- Комментарии для группировки логических блоков элементов
- Комментарии для проблемных элементов (disabled, hidden и т.д.)

**Форматирование:**
- Python PEP 8 (4 пробела отступ)
- Максимальная длина строки: 100 символов
- Двойные кавычки для строк
- f-strings где нужна интерполяция

---

## 8. Обработка ошибок и проблемного HTML

### Обработка malformed HTML

**Поведение:**
- ✅ Использовать `html5lib` парсер (понимает сломанный HTML)
- ✅ Автоматически "закрывать" незакрытые теги
- ✅ Обрабатывать неправильный порядок закрытия тегов
- ✅ Сохранять максимум информации

**Пример:**
```html
<button>Login
<input type="email">
```

Генератор исправит и обработает как:
```html
<button>Login</button>
<input type="email" />
```

### Специальные случаи

#### Пустой HTML
```html
<!-- пусто -->
```
**Выход**: Класс с пустым `__init__` и предупреждением в консоли
```
⚠️ Warning: No interactive elements found in HTML
```

#### Только текстовый контент
```html
<p>Hello World</p>
```
**Выход**: Только текстовый элемент (если считается значимым)
```python
self.hello_world_text = page.get_by_text("Hello World")
```

#### Дублирующиеся ID
```html
<button id="btn">Button 1</button>
<button id="btn">Button 2</button>  <!-- Дублируется! -->
```
**Выход**: Предупреждение + использование nth()
```
⚠️ Warning: Duplicate ID 'btn' detected. Using positional selector.

self.button_1 = page.locator("#btn").nth(0)
self.button_2 = page.locator("#btn").nth(1)
```

#### Элементы без идентификаторов
```html
<div><button></button></div>
<div><button></button></div>
```
**Выход**: С использованием XPath и warning
```
⚠️ Warning: Button at index 0 has no stable locator. Using XPath.

self.button_1 = page.locator("//button[1]")  # Может быть нестабильна
self.button_2 = page.locator("//button[2]")
```

### Скрытые и отключённые элементы

#### Скрытые элементы (display: none)
```html
<button style="display: none;">Hidden</button>
```
**Поведение**: ПРОПУСКАЕТСЯ (не создаётся свойство)

#### Отключённые элементы
```html
<input disabled>
<button disabled>Submit</button>
```
**Поведение**: Создаётся с комментарием
```python
# disabled
self.submit_button = page.get_by_role("button", name="Submit")
```

### Ошибки генерации

#### Невалидный class_name
```
❌ Error: class_name must be in PascalCase and start with a letter
Given: '123invalid'
```

#### Невалидный путь к файлу
```
❌ Error: File not found: /path/to/nonexistent.html
```

#### Неподдерживаемый формат
```
❌ Error: File format not supported. Expected .html
Given: file.txt
```

---

## 9. CLI

### Команда и опции

```bash
python main.py [OPTIONS]
```

### Опции

| Опция | Короткая | Тип | Обязательная | Описание |
|-------|----------|-----|-------------|----------|
| `--input` | `-i` | PATH | ✅ | Путь к HTML файлу или `-` для stdin |
| `--class-name` | `-c` | TEXT | ✅ | Имя класса (PascalCase) |
| `--output` | `-o` | PATH | ❌ | Путь для сохранения (.py файл). По умолчанию выводит в stdout |
| `--help` | `-h` | - | ❌ | Показать справку |

### Примеры использования

#### Из файла с сохранением
```bash
python main.py -i login.html -c LoginPage -o login_page.py
```

#### Из файла с выводом в консоль
```bash
python main.py -i login.html -c LoginPage
```

#### Из stdin
```bash
cat login.html | python main.py -c LoginPage -o login_page.py
```

#### Из stdin с выводом в консоль
```bash
echo "<button>Test</button>" | python main.py -c TestPage
```

#### Справка
```bash
python main.py --help
```

### Вывод --help

```
Usage: main.py [OPTIONS]

  Playwright Page Object Generator - convert HTML to Playwright Page Objects

Options:
  -i, --input PATH       Path to HTML file or - for stdin (stdin is default)  [required]
  -c, --class-name TEXT  Page class name in PascalCase (e.g., LoginPage)      [required]
  -o, --output PATH      Output file path (default: stdout)
  -h, --help             Show this message and exit.

Examples:
  python main.py -i login.html -c LoginPage -o login_page.py
  cat login.html | python main.py -c LoginPage
```

### Exit codes

| Код | Значение | Пример |
|-----|----------|--------|
| 0 | Успех | Файл сгенерирован |
| 1 | Ошибка | Невалидный HTML, файл не найден |
| 2 | Ошибка параметров | Отсутствует обязательный параметр |

---

## 10. Что входит в MVP (Minimum Viable Product)

### Функциональность MVP

✅ **Обязательно в MVP:**

1. **Парсинг HTML**
   - Читать HTML из файла или строки
   - Обрабатывать сломанный HTML (html5lib)
   - Исключать script/style теги

2. **Поддержка элементов (базовые)**
   - button, input (text, email, password, checkbox, radio)
   - textarea, select, label, form, a, h1-h6
   - div, span (с текстом)

3. **Локаторы (приоритет 1-6)**
   - get_by_role()
   - get_by_label()
   - get_by_placeholder()
   - get_by_text()
   - locator() с CSS
   - Базовый fallback (без XPath в MVP)

4. **Именование**
   - Преобразование в snake_case
   - Удаление спецсимволов
   - Обработка дублей (простый счётчик)

5. **Генерация кода**
   - Создание класса Page Object
   - Метод `__init__` с page параметром
   - Свойства для каждого элемента
   - Базовое форматирование

6. **CLI (базовый)**
   - Чтение из файла (-i)
   - Имя класса (-c)
   - Сохранение в файл (-o)
   - Вывод в stdout

7. **Тестирование**
   - Юнит-тесты для основных компонентов
   - Примеры HTML-файлов

### Не входит в MVP

❌ **Исключается из MVP:**

- XPath локаторы (только CSS в MVP)
- Web UI / GUI
- Валидация против живой страницы
- Генерация тестовых методов
- Поддержка других фреймворков (Selenium, Cypress)
- Конфигурационные файлы
- Плагины и расширения
- Shadow DOM обработка
- Интеграция с IDE

---

## 11. Что НЕ входит в MVP

- Web интерфейс для preview HTML
- Генерация тестов (test methods)
- XPath локаторы (только CSS fallback в MVP)
- Поддержка Selenium, Cypress
- Валидация локаторов на живой странице
- Custom configuration файлы
- Полная поддержка всех ARIA атрибутов
- Интеграция с CI/CD
- VS Code расширение
- Поддержка динамического контента (JavaScript-сгенерированного)

---

## 12. Acceptance Criteria

### Критерии приёма (когда MVP готов)

#### ✅ Базовая функциональность

- [ ] Генератор парсит простой HTML без ошибок
- [ ] Генерирует валидный Python код (синтаксис проверяется)
- [ ] Созданный Page Object класс можно импортировать и использовать
- [ ] Все свойства страницы правильно обозначены (имена в snake_case)

#### ✅ Локаторы

- [ ] Для button с текстом используется `get_by_role("button", name=...)`
- [ ] Для input с label используется `get_by_label(...)`
- [ ] Для input с placeholder используется `get_by_placeholder(...)`
- [ ] Для элементов с ID используется `locator("#id")`
- [ ] Все локаторы точны и найдут нужный элемент

#### ✅ HTML обработка

- [ ] Обрабатывает сломанный HTML (незакрытые теги)
- [ ] Исключает script и style теги
- [ ] Пропускает скрытые элементы
- [ ] Добавляет комментарии для disabled элементов

#### ✅ Именование

- [ ] Имена в snake_case
- [ ] Имена включают тип элемента (input, button, link и т.д.)
- [ ] Дублирующиеся имена обрабатываются (добавляется индекс)
- [ ] Спецсимволы удаляются или заменяются

#### ✅ CLI

- [ ] `python main.py -i file.html -c PageName` работает
- [ ] `-o` опция сохраняет результат в файл
- [ ] Без `-o` выводит в stdout
- [ ] `--help` показывает справку
- [ ] Обработка ошибок (файл не найден, неправильные параметры)

#### ✅ Тестирование

- [ ] Минимум 80% code coverage
- [ ] Тесты покрывают основные сценарии
- [ ] Тесты для edge cases (пустой HTML, дублирующиеся элементы)
- [ ] Все тесты проходят (pytest)

#### ✅ Документация

- [ ] README.md с примерами использования
- [ ] Docstrings во всех классах и методах
- [ ] CLAUDE.md актуален
- [ ] Примеры HTML-файлов в папке examples/

#### ✅ Код качество

- [ ] Проходит flake8 проверку
- [ ] Имеет type hints для всех функций
- [ ] Отформатирован с помощью black
- [ ] Нет непроходящих mypy проверок

#### ✅ Примеры работы

- [ ] Пример 1: Простая форма Login (email, password, button)
- [ ] Пример 2: Контактная форма (多 input, textarea, button)
- [ ] Пример 3: Сложная структура (nested elements, table)
- [ ] Все примеры генерируют валидный Python код

---

## Нужно решить

### Нерешённые вопросы / Предположения

#### 1. Обработка повторяющихся элементов без идентификаторов
**Вопрос**: Как именовать кнопки без текста в одной форме?
```html
<button></button>
<button></button>
```

**Вариант A**: `button_1`, `button_2` (простой счётчик)  
**Вариант B**: `first_button`, `second_button`  
**Текущее решение**: Вариант A + warning о нестабильности

**Решение нужно**: ДА/НЕТ / Другое предложение

---

#### 2. Обработка элементов с очень длинным текстом
**Вопрос**: Как сократить имя свойства для элемента?
```html
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
```

**Вариант A**: Использовать первые N слов  
**Вариант B**: Создать generic имя (paragraph_1)  
**Вариант C**: Пропустить элемент

**Текущее решение**: Вариант B

---

#### 3. Поддержка data-testid vs других data-* атрибутов
**Вопрос**: Использовать ли другие data-* атрибуты для локаторов?
```html
<button data-qa="submit-btn">Submit</button>  <!-- data-qa -->
<button data-testid="submit">Submit</button>  <!-- data-testid -->
```

**Вариант A**: Только data-testid  
**Вариант B**: Все data-* атрибуты

**Текущее решение**: Только data-testid

---

#### 4. Комментарии в генерируемом коде
**Вопрос**: Добавлять ли комментарии в сгенерированный код?
```python
# Вариант A: Без комментариев
self.login_button = page.get_by_role("button", name="Login")

# Вариант B: С описанием
# Login button - triggers form submission
self.login_button = page.get_by_role("button", name="Login")
```

**Текущее решение**: Только для проблемных элементов (disabled)

---

#### 5. Обработка SVG и Canvas
**Вопрос**: Обрабатывать ли SVG и Canvas элементы?
```html
<svg><button>Click</button></svg>
<canvas></canvas>
```

**Вариант A**: Игнорировать  
**Вариант B**: Парсить содержимое

**Текущее решение**: Игнорировать (в MVP)

---

#### 6. Максимальная вложенность элементов
**Вопрос**: Есть ли ограничение на обработку глубоко вложенных элементов?

**Текущее решение**: Нет ограничений

---

#### 7. Кодировка файлов
**Вопрос**: Какую кодировку использовать при чтении/записи файлов?

**Текущее решение**: UTF-8

---

#### 8. Вывод предупреждений и логов
**Вопрос**: Куда выводить warning'и (stdout, stderr, логи)?

**Вариант A**: В stderr (отдельно от результата)  
**Вариант B**: В stdout (в комментариях кода)  
**Вариант C**: В отдельный лог-файл

**Текущее решение**: Вариант A (stderr)


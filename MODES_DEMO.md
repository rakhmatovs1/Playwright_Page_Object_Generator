# Playwright Page Object Generator - All Modes Demo

## ✅ Режим 1: Interactive Mode (Интерактивный режим)

**Идеально для новичков и быстрого прототипирования**

```bash
python main.py -I
```

или

```bash
python main.py --interactive
```

**Диалог:**
```
=== Playwright Page Object Generator (Interactive Mode) ===

[1/3] Enter HTML file path (or - for stdin): examples/sample_login.html
[2/3] Enter class name (PascalCase, e.g., LoginPage): LoginPage  
[3/3] Output file path (press Enter for stdout): login_page.py

class LoginPage:
    ...
```

---

## ✅ Режим 2: File → File (Файл в файл)

**Для production скриптов и CI/CD**

```bash
python main.py -i examples/sample_login.html -c LoginPage -o login_page.py
```

**Результат:**
```
Generated: login_page.py
```

---

## ✅ Режим 3: File → Stdout (Файл в консоль)

**Для быстрого превью**

```bash
python main.py -i examples/sample_login.html -c LoginPage
```

**Результат:**
```
class LoginPage:
    """Page Object for login page page."""
    
    def __init__(self, page):
        ...
```

---

## ✅ Режим 4: Stdin → File (Консоль в файл)

**Для pipeline обработки**

```bash
cat examples/sample_login.html | python main.py -c LoginPage -o login_page.py
```

или

```bash
echo "<button>Click</button>" | python main.py -c ButtonPage -o button_page.py
```

---

## ✅ Режим 5: Stdin → Stdout (Консоль в консоль)

**Для цепочки команд**

```bash
cat examples/sample_login.html | python main.py -c LoginPage
```

**Результат:**
```
class LoginPage:
    ...
```

---

## 📊 Сравнение режимов

| Режим | Команда | Лучше для | Требует |
|-------|---------|----------|---------|
| **Interactive** | `main.py -I` | Новичков, одноразово | Ничего |
| **File→File** | `main.py -i in.html -c Name -o out.py` | Production, CI/CD | `-i -c -o` |
| **File→Stdout** | `main.py -i in.html -c Name` | Превью кода | `-i -c` |
| **Stdin→File** | `cat in.html \| main.py -c Name -o out.py` | Pipelines | `-c -o` |
| **Stdin→Stdout** | `cat in.html \| main.py -c Name` | Цепочки команд | `-c` |

---

## 🎯 Быстрые примеры

```bash
# 1. Интерактивно (для новичка)
python main.py -I

# 2. От файла (для production)
python main.py -i pages/login.html -c LoginPage -o login_page.py

# 3. Превью (для проверки)
python main.py -i pages/login.html -c LoginPage

# 4. Из pipe (для scripts)
ls *.html | xargs -I {} python main.py -i {} -c MyPage -o pages/{.}_obj.py

# 5. Help (если забыл)
python main.py --help
```

---

## 📝 Результат для всех режимов

Все режимы производят **одинаковый результат** - валидный Python код:

```python
class LoginPage:
    """Page Object for login page."""

    def __init__(self, page):
        """Initialize page object with Playwright page instance."""
        self.page = page

        # Buttons
        self.login_button = page.get_by_role("button", name="Login")

        # Inputs
        self.email_input = page.get_by_label("Email Address")
        self.password_input = page.get_by_label("Password")
```

Отличаются только **входные/выходные механизмы**! 🎉

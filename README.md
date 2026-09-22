# Playwright Page Object Generator

🚀 **Automatically generate Playwright Page Object classes from HTML!**

Transform raw HTML → intelligent Python Page Objects with best-practice Playwright locators in seconds.

## What It Does

```
Input: HTML (file or string)
         ↓
    [Generate Page Object]
         ↓
Output: Python class with optimized locators
```

**Example:**
```html
<!-- Input HTML -->
<button>Login</button>
<input type="email" placeholder="Email">
```

↓ **Becomes:** ↓

```python
# Generated Python
class LoginPage:
    def __init__(self, page):
        self.login_button = page.get_by_role("button", name="Login")
        self.email_input = page.get_by_placeholder("Email")
```

---

## Quick Start (5 minutes)

### 1️⃣ Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Generate Your First Page Object

**Option A: Interactive Mode (recommended for beginners)**
```bash
python main.py --interactive
# or just:
python main.py -I

# Then answer the 3 questions:
# [1/3] Enter HTML file path: examples/sample_login.html
# [2/3] Enter class name: LoginPage
# [3/3] Output file path: login_page.py
```

**Option B: Command Line (faster for scripts)**
```bash
# From an HTML file → save to Python file
python main.py -i examples/sample_login.html -c LoginPage -o login_page.py

# Preview in terminal (no -o flag)
python main.py -i examples/sample_login.html -c LoginPage

# From stdin
cat examples/sample_login.html | python main.py -c LoginPage
```

That's it! ✅ You now have a ready-to-use Page Object.

---

## More Usage Examples

### Installation (if not done already)

```bash
pip install -r requirements.txt
```

### Operation Modes

| Mode | Command | Use Case | Requires |
|------|---------|----------|----------|
| **Interactive** | `main.py -I` | Beginners, one-off generation | Nothing |
| **File → File** | `main.py -i in.html -c Name -o out.py` | Production, CI/CD | `-i -c -o` |
| **File → Stdout** | `main.py -i in.html -c Name` | Preview code | `-i -c` |
| **Stdin → File** | `cat in.html \| main.py -c Name -o out.py` | Pipelines | `-c -o` |
| **Stdin → Stdout** | `cat in.html \| main.py -c Name` | Command chains | `-c` |

### Command Line Examples

```bash
# Interactive mode (ask me questions)
python main.py -I

# 📄 File → File (save to Python file)
python main.py -i login.html -c LoginPage -o login_page.py

# 📺 File → Stdout (preview in terminal)
python main.py -i login.html -c LoginPage

# 📥 Stdin → File (pipe HTML from another command)
cat login.html | python main.py -c LoginPage -o login_page.py

# 📥 Stdin → Stdout (full pipeline)
cat login.html | python main.py -c LoginPage

# ❓ Get help
python main.py --help
```

### Use as Python Library

```python
from src.generator import PageObjectGenerator

generator = PageObjectGenerator()

# Generate from HTML string
po_code = generator.generate(
    html='<button>Login</button><input type="email" placeholder="Email">',
    class_name='LoginPage'
)
print(po_code)

# Generate from file
po_code = generator.generate_from_file(
    filepath='login.html',
    class_name='LoginPage'
)

# Save to file
generator.save_to_file(po_code, 'login_page.py')
```

---

---

## Learn More

📖 **Architecture & design:** See `CLAUDE.md`

## Testing

Run tests with pytest:

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_parser.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
.
├── main.py                      # CLI entry point
├── requirements.txt             # Dependencies
├── src/
│   ├── __init__.py
│   ├── parser.py               # HTML parsing
│   ├── locator_selector.py     # Locator strategy
│   ├── generator.py            # Code generation
│   ├── utils.py                # Naming, formatting
│   └── cli.py                  # Command-line interface
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_parser.py          # Parser tests
│   ├── test_locator_selector.py # Locator tests
│   ├── test_utils.py           # Utility tests
│   ├── test_generator.py       # Generator tests
│   ├── test_cli.py             # CLI tests
│   └── test_integration.py     # Integration tests
└── README.md                   # This file
```

## CLI Reference

### Options

| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--interactive` | `-I` | - | ❌ | Interactive mode (ask questions) |
| `--input` | `-i` | PATH | ⚠️ | HTML file path or `-` for stdin (required without `-I`) |
| `--class-name` | `-c` | TEXT | ⚠️ | Page class name (PascalCase, required without `-I`) |
| `--output` | `-o` | PATH | ❌ | Output file path (default: stdout) |
| `--help` | `-h` | - | ❌ | Show help message |

### Exit Codes

- `0` - Success
- `1` - Runtime error (invalid HTML, file not found, etc.)
- `2` - Invalid command-line arguments

## License

MIT

## Changelog

### v0.1.0 (MVP)
- HTML parsing with BeautifulSoup
- 7-step priority-based locator selection
- snake_case property naming
- PEP 8 formatted output
- CLI with file and stdin support
- 261 comprehensive tests

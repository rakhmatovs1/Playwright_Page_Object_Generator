# Input/Output Спецификация

## 📥 INPUT → 📤 OUTPUT

---

## 1. UTILS FUNCTIONS

### `to_snake_case(input_name: str) → str`

| Input | Output |
|-------|--------|
| `"loginButton"` | `"login_button"` |
| `"LoginButton"` | `"login_button"` |
| `"login_button"` | `"login_button"` |
| `"button"` | `"button"` |
| `"Button"` | `"button"` |
| `"HTMLParser"` | `"html_parser"` |
| `"XMLElement"` | `"xml_element"` |
| `"IODevice"` | `"io_device"` |

---

### `add_element_type_suffix(description: str, element_type: str) → str`

| Description | Type | Output |
|-------------|------|--------|
| `"Login"` | `"button"` | `"login_button"` |
| `"Email"` | `"input"` | `"email_input"` |
| `"Home"` | `"link"` | `"home_link"` |
| `"Main Title"` | `"heading"` | `"main_title_heading"` |
| `"Login"` | `"form"` | `"login_form"` |
| `"Remember me"` | `"checkbox"` | `"remember_me_checkbox"` |
| `"Error message"` | `"text"` | `"error_message_text"` |

---

### `remove_special_characters(text: str) → str`

| Input | Output |
|-------|--------|
| `"Sign-Up"` | `"Sign Up"` |
| `"Email Address"` | `"Email Address"` |
| `"Sign-Up & Continue"` | `"Sign Up and Continue"` |
| `"Email (required)"` | `"Email required"` |
| `"Username/Email"` | `"Username Email"` |
| `"Cost: $99.99"` | `"Cost 99.99"` |
| `"👍 Like"` | `"Like"` |

---

### `generate_name_from_attributes(element: dict) → str`

| Attribute | Value | Type | Output |
|-----------|-------|------|--------|
| `placeholder` | `"Email"` | `"input"` | `"email_input"` |
| `aria-label` | `"Close dialog"` | `"button"` | `"close_dialog_button"` |
| `text` | `"Login"` | `"button"` | `"login_button"` |
| `text` | `"Profile"` | `"link"` | `"profile_link"` |
| `text` | `"Welcome"` | `"heading"` | `"welcome_heading"` |

---

### `handle_duplicate_names(names: list) → dict`

| Input | Output |
|-------|--------|
| `["button", "button"]` | `{"button_0": "button_1", "button_1": "button_2"}` |
| `["email_input", "password_input"]` | `{"email_input": "email_input", "password_input": "password_input"}` |
| `["login", "login", "login"]` | `{"login_0": "login_1", "login_1": "login_2", "login_2": "login_3"}` |

---

### `is_valid_python_identifier(name: str) → bool`

| Input | Output | Reason |
|-------|--------|--------|
| `"123invalid"` | `False` | starts with digit |
| `"class"` | `False` | Python keyword |
| `"def"` | `False` | Python keyword |
| `"if"` | `False` | Python keyword |
| `"_private_element"` | `True` | valid |
| `"login_button"` | `True` | valid |
| `"element_123"` | `True` | valid |

---

### `format_code_line(code: str, indent: int = 0) → str`

| Input | Indent | Output |
|-------|--------|--------|
| `"self.button = page.get_by_role('button')"` | 0 | `"self.button = page.get_by_role('button')"` |
| `"self.button = page.get_by_role('button')"` | 1 | `"    self.button = page.get_by_role('button')"` |
| `"self.button = page.get_by_role('button')"` | 2 | `"        self.button = page.get_by_role('button')"` |

---

## 2. PARSER

### `HTMLParser.parse(html: str) → List[Dict]`

**Input:**
```html
<button>Login</button>
<input type="email" placeholder="Email">
<form id="loginForm">
    <label for="password">Password</label>
    <input id="password" type="password">
</form>
```

**Output (List of elements):**
```python
[
    {
        "tag": "button",
        "text": "Login",
        "type": "button"
    },
    {
        "tag": "input",
        "type": "email",
        "placeholder": "Email"
    },
    {
        "tag": "form",
        "id": "loginForm"
    },
    {
        "tag": "label",
        "for": "password",
        "text": "Password"
    },
    {
        "tag": "input",
        "id": "password",
        "type": "password"
    }
]
```

---

### `HTMLParser.parse_file(filepath: str) → List[Dict]`

**Input:** `"/path/to/login.html"`

**Output:** Same as `parse()` - list of elements

---

## 3. LOCATOR SELECTOR

### `LocatorSelector.select_locator(element: dict) → dict`

#### Priority Strategy (шаги 1-7):

| Element | Step | Locator Output |
|---------|------|-----------------|
| `{"tag": "button", "text": "Login"}` | 1 (role) | `{"method": "get_by_role", "role": "button", "name": "Login"}` |
| `{"tag": "input", "aria_label": "Email"}` | 2 (aria-label) | `{"method": "get_by_label", "label": "Email"}` |
| `{"tag": "input", "placeholder": "Search"}` | 4 (placeholder) | `{"method": "get_by_placeholder", "placeholder": "Search"}` |
| `{"tag": "button", "text": "Submit"}` | 5 (text) | `{"method": "get_by_text", "text": "Submit"}` |
| `{"tag": "input", "id": "email"}` | 6 (id) | `{"method": "locator", "selector": "#email"}` |
| `{"tag": "button", "class": ["btn", "primary"]}` | 7 (css class) | `{"method": "locator", "selector": "button.btn.primary"}` |

---

## 4. PAGE OBJECT GENERATOR

### `PageObjectGenerator.generate(html: str, class_name: str) → str`

**Input:**
```python
html = """
<form id="loginForm">
    <h1>Sign In</h1>
    <label for="email">Email Address</label>
    <input id="email" type="email" required>
    <label for="password">Password</label>
    <input id="password" type="password" required>
    <button type="submit">Sign In</button>
</form>
"""
class_name = "LoginPage"
```

**Output (Python code string):**
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
        
        # Buttons
        self.sign_in_button = page.get_by_role("button", name="Sign In")
```

---

### `PageObjectGenerator.generate_from_file(filepath: str, class_name: str) → str`

**Input:**
```python
filepath = "login.html"
class_name = "LoginPage"
```

**Output:** Same as `generate()` - Python code string

---

### `PageObjectGenerator.save_to_file(code: str, filepath: str) → None`

**Input:**
```python
code = "class LoginPage: ..."
filepath = "login_page.py"
```

**Output:** File created at `login_page.py` with the code

---

### `PageObjectGenerator.validate_class_name(class_name: str) → bool`

| Input | Output |
|-------|--------|
| `"LoginPage"` | `True` |
| `"CheckoutPage"` | `True` |
| `"loginpage"` | `False` |
| `"login_page"` | `False` |
| `"123Invalid"` | `False` |

---

## 5. CLI

### `python main.py -i <input> -c <class> [-o <output>]`

#### Example 1: File to File

**Input:**
```bash
python main.py -i login.html -c LoginPage -o login_page.py
```

**Output:** File `login_page.py` created with Page Object code

---

#### Example 2: File to Stdout

**Input:**
```bash
python main.py -i login.html -c LoginPage
```

**Output (stdout):**
```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        ...
```

---

#### Example 3: Stdin to File

**Input:**
```bash
cat login.html | python main.py -c LoginPage -o login_page.py
```

**Output:** File `login_page.py` created

---

#### Example 4: Stdin to Stdout

**Input:**
```bash
echo "<button>Test</button>" | python main.py -c TestPage
```

**Output (stdout):**
```python
class TestPage:
    def __init__(self, page):
        self.page = page
        self.test_button = page.get_by_role("button", name="Test")
```

---

## 6. END-TO-END FLOW

```
┌─────────────────┐
│  INPUT HTML     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ HTMLParser.parse()          │
│ Extract elements & attrs    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ For each element:                   │
│ LocatorSelector.select_locator()    │
│ Choose best Playwright locator      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ For each element:                   │
│ Utils: generate_name_from_attributes│
│ Create snake_case property name     │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ PageObjectGenerator.generate()      │
│ Build Python Page Object class      │
└────────┬────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ OUTPUT: Python Page Object   │
│ - Valid Python syntax        │
│ - Playwright locators        │
│ - snake_case properties      │
│ - Proper formatting          │
└──────────────────────────────┘
```

---

## 7. ERROR HANDLING

### Invalid Inputs

| Input | Error | Exit Code |
|-------|-------|-----------|
| No `--input` | "Missing required option '--input'" | 2 |
| No `--class-name` | "Missing required option '--class-name'" | 2 |
| File not found | "File not found: /path/to/file.html" | 1 |
| Invalid class name | "class_name must be in PascalCase" | 1 |
| Malformed HTML | Still parses (html5lib auto-corrects) | 0 |

---

## 8. PARAMETRIZED TEST EXAMPLES

### snake_case conversion (8 cases)
```python
@pytest.mark.parametrize("input_name,expected", [
    ("loginButton", "login_button"),
    ("LoginButton", "login_button"),
    ("login_button", "login_button"),
    ("button", "button"),
    ("Button", "button"),
    ("HTMLParser", "html_parser"),
    ("XMLElement", "xml_element"),
    ("IODevice", "io_device"),
])
def test_convert_to_snake_case(input_name, expected):
    result = to_snake_case(input_name)
    assert result == expected
```

### Element type suffixes (7 cases)
```python
@pytest.mark.parametrize("description,element_type,expected", [
    ("Login", "button", "login_button"),
    ("Email", "input", "email_input"),
    ("Home", "link", "home_link"),
    ("Main Title", "heading", "main_title_heading"),
    ("Login", "form", "login_form"),
    ("Remember me", "checkbox", "remember_me_checkbox"),
    ("Error message", "text", "error_message_text"),
])
def test_add_element_type_suffix(description, element_type, expected):
    result = add_element_type_suffix(description, element_type)
    assert result == expected
```

---

## 📋 SUMMARY

```
Total Input/Output Specifications:
  - Utils functions:     7 функций × 5-30 cases each
  - Parser:              2 методов
  - Locator Selector:    7 priority steps + CSS fallback
  - Generator:           4 методов
  - CLI:                 4 основных workflows + error cases
  - End-to-End:          Complete flow diagram
```

All specifications match REQUIREMENTS.md and drive the TDD implementation!

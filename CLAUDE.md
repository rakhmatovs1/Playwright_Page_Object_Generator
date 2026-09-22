# Playwright Page Object Generator

## Project Overview

A Python-based QA Automation utility that automatically generates Playwright Page Object classes from HTML code or files. The generated Page Objects use stable, readable, and maintainable locators following Playwright best practices.

**Language**: Python (generates Python code for Playwright)  
**Type**: Homework project for AI Seminar  

## Setup & Environment

### Virtual Environment Requirement
This project **MUST** use a Python virtual environment. This is mandatory for all development, testing, and deployment.

**Setup steps:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Important:**
- ✅ Always activate venv before running any Python code
- ✅ Always run tests within activated venv
- ✅ Always run CLI commands within activated venv
- ❌ Never install packages globally
- ❌ Never commit venv/ directory to git

**Git configuration:**
Add to `.gitignore`:
```
venv/
```

---

## Purpose & Goals

Transform raw HTML → intelligent Playwright Page Object classes with:
- ✅ Stable, semantically-correct locators
- ✅ Readable property names following naming conventions
- ✅ Maintainable code structure
- ✅ WCAG/accessibility-first approach to element selection

### Example

**Input (HTML)**:
```html
<input type="email" placeholder="Email">
<button>Login</button>
<form id="loginForm">
  <label for="password">Password</label>
  <input id="password" type="password">
</form>
```

**Output (Python Page Object for Playwright)**:
```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.email_input = page.get_by_placeholder("Email")
        self.login_button = page.get_by_role("button", name="Login")
        self.password_input = page.locator("#password")
        self.login_form = page.locator("#loginForm")
```

## Project Architecture

### Directory Structure

```
.
├── CLAUDE.md                    # Project guidelines
├── README.md                    # User documentation & examples
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── src/
│   ├── __init__.py
│   ├── parser.py                # HTML parsing & tree building
│   ├── locator_selector.py      # Locator strategy selection logic
│   ├── generator.py             # Page Object code generation
│   └── utils.py                 # Helpers: naming, formatting
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_locator_selector.py
│   └── test_generator.py
└── examples/
    └── sample_login.html
```

### Data Flow

```
Input HTML
    ↓
Parser (BeautifulSoup)
    ↓
Element Analysis
    ├─ Extract attributes
    ├─ Identify type & context
    └─ Analyze accessibility
    ↓
Locator Selection
    ├─ Priority-based strategy
    └─ Generate Playwright locator syntax
    ↓
Code Generation
    ├─ Build class structure
    ├─ Format property names
    └─ Output Python code
```

## Locator Selection Strategy

Locators are selected in priority order for **stability** and **maintainability**:

1. **`get_by_role()`** - Best practice, WCAG-aligned, most stable
   - Buttons, links, headings, form fields with semantic meaning
   - Example: `page.get_by_role("button", name="Login")`

2. **`get_by_label()`** - For form inputs with associated labels
   - Example: `page.get_by_label("Email")`

3. **`get_by_placeholder()`** - For input fields with placeholders
   - Example: `page.get_by_placeholder("Enter email")`

4. **`get_by_text()`** - For elements with visible text content
   - Example: `page.get_by_text("Submit", exact=True)`

5. **`locator()`** with CSS/XPath - Fallback for complex scenarios
   - Use only when other methods are unavailable
   - Prefer CSS selectors over XPath

### Locator Quality Scoring

For each element, evaluate in order:
- Does it have `role` attribute or semantic HTML? → use `get_by_role()`
- Does it have `aria-label` or `for` attribute? → use `get_by_label()`
- Does it have `placeholder`? → use `get_by_placeholder()`
- Does it have meaningful text content? → use `get_by_text()`
- Does it have `id` or stable `data-testid`? → use `locator()`

## Naming Conventions

### Property Names
- **Format**: `snake_case` (Python convention)
- **Pattern**: `{description}_{element_type}`
- **Examples**:
  - `email_input` (input field for email)
  - `login_button` (button for login action)
  - `password_field` (password input)
  - `submit_button` (submit action button)
  - `error_message` (error text/alert)
  - `search_form` (form container)

### Class Names
- **Format**: `{PageName}Page`
- **Examples**: `LoginPage`, `CheckoutPage`, `ProfileSettingsPage`
- Generated from filename or user input

### File Naming
- Generated files: `{page_name}_page.py` (snake_case)
- Example: `login_page.py` for `LoginPage` class

## Dependencies

```
beautifulsoup4>=4.11.0      # HTML parsing
html5lib>=1.1               # Flexible HTML5 parser
playwright>=1.40.0          # For locator reference (types, examples)
```

## Usage Scenarios

### Command Line
```bash
python main.py --input path/to/page.html --output path/to/login_page.py --class-name LoginPage
```

### As Module
```python
from src.generator import PageObjectGenerator

generator = PageObjectGenerator()

# From HTML string
po_code = generator.generate(
    html='<button>Login</button>',
    class_name='LoginPage'
)
print(po_code)

# From file
po_code = generator.generate_from_file(
    filepath='login.html',
    class_name='LoginPage'
)
```

## Code Quality Rules

### General
- Type hints for all function signatures
- Docstrings for classes and public methods
- Clear variable names - avoid abbreviations
- Maximum line length: 100 characters

### HTML Parsing
- Handle malformed HTML gracefully (use `html5lib`)
- Ignore script and style tags
- Preserve element hierarchy context

### Locator Generation
- Always prefer accessibility-first approach
- Skip hidden/disabled elements
- Handle dynamic attributes (data-* not guaranteed stable)
- Add comments for non-obvious locators

### Output Code
- Generated Python must be executable
- Use f-strings for formatting
- Include docstrings explaining element purpose
- Proper indentation (4 spaces)

## Testing Strategy

### Unit Tests Cover
- ✅ HTML parsing with various structures
- ✅ Locator selection logic for each strategy
- ✅ Naming convention edge cases
- ✅ Code generation and formatting
- ✅ Error handling for malformed HTML

### Test Data
- Simple forms (login, contact)
- Complex nested structures
- Tables and lists
- Dynamic elements with data attributes
- Accessibility features (ARIA labels, roles)

## Edge Cases to Handle

1. **Multiple elements with same text** → Add index/position to name
2. **Elements with no identifiable locator** → Use XPath with warning
3. **Duplicate property names** → Append counter (e.g., `button_1`, `button_2`)
4. **Special characters in labels** → Sanitize for valid Python identifiers
5. **Hidden/disabled elements** → Skip or include with comment
6. **Empty or very short labels** → Use element type + generic name

## Future Enhancements

- [ ] Support for other frameworks (Selenium, Cypress)
- [ ] Web UI for real-time HTML preview
- [ ] Configuration file for custom rules
- [ ] Integration with IDE (VS Code extension)
- [ ] Auto-generated test templates
- [ ] Locator validation against live page

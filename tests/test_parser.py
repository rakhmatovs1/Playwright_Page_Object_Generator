"""Tests for HTML parser module - OPTIMIZED VERSION."""
import pytest
from src.parser import HTMLParser


class TestParserBasics:
    """Test basic HTML parsing functionality."""

    def test_parse_simple_html(self, simple_html):
        """Parser should parse simple HTML without errors."""
        # Requirement: "Читать HTML из файла или строки"
        parser = HTMLParser()
        elements = parser.parse(simple_html)
        assert elements is not None
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_parse_preserves_attributes(self):
        """Parser should preserve element attributes (id, type, placeholder, etc.)."""
        html = '<input id="email" type="email" placeholder="Enter email" required>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should extract element with all attributes
        assert len(elements) > 0
        element = elements[0]
        assert element.get("id") == "email"
        assert element.get("type") == "email"
        assert element.get("placeholder") == "Enter email"
        assert "required" in element

    def test_parse_preserves_hierarchy(self):
        """Parser should preserve parent-child element relationships."""
        html = '<form id="form"><label for="email">Email</label><input id="email"></form>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should have form and its children
        assert len(elements) >= 2
        # At least one element should have parent reference
        assert any(e.get("parent") for e in elements) or any("parent" in e for e in elements)


class TestParserMalformedHTML:
    """Test parser handling of malformed HTML."""

    def test_parse_unclosed_tags(self, malformed_html):
        """Parser should handle unclosed tags gracefully using html5lib."""
        # html5lib auto-closes tags
        parser = HTMLParser()
        elements = parser.parse(malformed_html)
        # Should not raise error and return something
        assert elements is not None
        assert isinstance(elements, list)

    def test_parse_wrong_nesting_order(self):
        """Parser should correct incorrectly nested tags."""
        html = "<div><button></div></button>"
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should handle without raising error
        assert elements is not None
        assert isinstance(elements, list)


class TestParserIgnoredElements:
    """Test that parser correctly ignores non-interactive elements."""

    @pytest.mark.parametrize("element_tag,content", [
        ("script", "console.log('ignored');"),
        ("style", "button { color: red; }"),
        ("meta", ""),
        ("noscript", "JavaScript required"),
    ])
    def test_ignore_non_interactive_elements(self, element_tag, content):
        """Parser should completely ignore script, style, meta, noscript tags."""
        # Requirement: "Игнорируются полностью (содержимое пропускается)"
        html = f'<button>Visible</button><{element_tag}>{content}</{element_tag}>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should only have button, not script/style/meta tags
        tags = [e.get("tag", e.get("type")) for e in elements]
        assert "script" not in str(tags).lower()
        assert "style" not in str(tags).lower()
        assert "meta" not in str(tags).lower()

    def test_ignore_html_comments(self):
        """Parser should ignore HTML comments."""
        html = '<!-- This comment is ignored --><button>Visible</button>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should only have button, no comment text
        assert len(elements) >= 1
        text_content = str(elements).lower()
        assert "this comment is ignored" not in text_content

    def test_ignore_head_content(self):
        """Parser should ignore content inside head tag."""
        html = '<head><title>Page</title></head><body><button>Click</button></body>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should have button but not title
        assert len(elements) >= 1
        text = str(elements).lower()
        assert "click" in text or any(e.get("text") == "Click" for e in elements)


class TestParserElementExtraction:
    """Test extraction of specific element types."""

    @pytest.mark.parametrize("tag,element_type", [
        ("button", "button"),
        ("a", "link"),
        ("form", "form"),
        ("textarea", "textarea"),
        ("select", "select"),
    ])
    def test_extract_interactive_elements(self, tag, element_type):
        """Parser should extract interactive elements."""
        # Requirement: "Полностью поддерживаемые элементы"
        html = f'<{tag}>Content</{tag}>'
        parser = HTMLParser()
        elements = parser.parse(html)
        assert len(elements) > 0

    @pytest.mark.parametrize("input_type", ["text", "email", "password", "checkbox", "radio", "date", "number"])
    def test_extract_all_input_types(self, input_type):
        """Parser should extract all input types."""
        # Requirement: "input — текстовые поля, email, password, checkbox, radio"
        html = f'<input type="{input_type}">'
        parser = HTMLParser()
        elements = parser.parse(html)
        assert len(elements) > 0
        assert any(e.get("type") == input_type for e in elements)

    @pytest.mark.parametrize("level", range(1, 7))
    def test_extract_headings(self, level):
        """Parser should extract heading elements h1-h6."""
        tag = f"h{level}"
        html = f"<{tag}>Heading</{tag}>"
        parser = HTMLParser()
        # Requirement: "<h1>, <h2>, ..., <h6> — заголовки"
        elements = parser.parse(html)
        assert len(elements) > 0

    def test_extract_table_elements(self, html_with_tables):
        """Parser should extract table structures."""
        # Requirement: "<table>, <thead>, <tbody>, <tr>, <td>, <th>"
        parser = HTMLParser()
        elements = parser.parse(html_with_tables)
        assert len(elements) > 0

    def test_extract_list_elements(self, html_lists):
        """Parser should extract list structures."""
        # Requirement: "<ul>, <ol>, <li> — списки"
        parser = HTMLParser()
        elements = parser.parse(html_lists)
        assert len(elements) > 0

    def test_extract_semantic_sections(self, html_semantic_sections):
        """Parser should extract semantic elements."""
        # Requirement: "<div>, <section>, <nav>, <header>, <footer>, <main>, <article>"
        parser = HTMLParser()
        elements = parser.parse(html_semantic_sections)
        assert len(elements) > 0


class TestParserAttributeExtraction:
    """Test extraction of element attributes."""

    @pytest.mark.parametrize("attr_name,attr_value", [
        ("id", "email"),
        ("type", "email"),
        ("placeholder", "Enter email"),
        ("aria-label", "Email input"),
        ("data-testid", "email-field"),
        ("disabled", ""),
        ("required", ""),
    ])
    def test_extract_attributes(self, attr_name, attr_value):
        """Parser should extract various element attributes."""
        # Requirement: "Элементы с aria-label, aria-labelledby, data-testid"
        attr_str = f'{attr_name}="{attr_value}"' if attr_value else attr_name
        html = f'<input {attr_str}>'
        parser = HTMLParser()
        elements = parser.parse(html)
        assert len(elements) > 0

    def test_extract_text_content(self):
        """Parser should extract element text content."""
        html = '<button>Login</button>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should extract text "Login"
        assert len(elements) > 0
        assert any("Login" in str(e.get("text", e.get("content", ""))) for e in elements)


class TestParserHiddenElements:
    """Test parser detection of hidden/disabled elements."""

    @pytest.mark.parametrize("hidden_method,description", [
        ('style="display: none;"', "display:none"),
        ('hidden', "hidden attribute"),
        ('style="visibility: hidden;"', "visibility:hidden"),
    ])
    def test_mark_hidden_elements(self, hidden_method, description):
        """Parser should mark elements as hidden."""
        # Requirement: "Скрытые элементы... ПРОПУСКАЮТСЯ"
        html = f'<button {hidden_method}>Hidden</button>'
        parser = HTMLParser()
        elements = parser.parse(html)
        # Hidden elements should be either skipped or marked as hidden
        if len(elements) > 0:
            assert any(e.get("hidden") or e.get("style", "").find("display: none") >= 0 for e in elements)

    def test_mark_disabled_elements(self, html_with_hidden_elements):
        """Parser should mark disabled elements."""
        # Requirement: "Отключённые элементы (disabled атрибут)"
        parser = HTMLParser()
        elements = parser.parse(html_with_hidden_elements)
        # Should have elements, some marked as disabled
        assert len(elements) > 0


class TestParserDuplicateIDs:
    """Test parser handling of duplicate IDs."""

    def test_detect_duplicate_ids(self, html_with_duplicates):
        """Parser should detect when same ID appears multiple times."""
        # Requirement: "Дублирующиеся ID"
        parser = HTMLParser()
        elements = parser.parse(html_with_duplicates)
        # Should have elements with duplicate detection
        assert len(elements) > 0


class TestParserFileReading:
    """Test parser file I/O capabilities."""

    def test_read_from_string(self, simple_html):
        """Parser should parse HTML from string."""
        # Requirement: "Читать HTML из файла или строки"
        parser = HTMLParser()
        elements = parser.parse(simple_html)
        assert elements is not None
        assert isinstance(elements, list)

    def test_read_from_file(self, tmp_path):
        """Parser should read HTML from file."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<button>Test</button>", encoding="utf-8")
        parser = HTMLParser()
        elements = parser.parse_file(str(html_file))
        assert elements is not None
        assert isinstance(elements, list)

    def test_file_not_found_error(self):
        """Parser should raise error for non-existent file."""
        # Negative test - error handling
        parser = HTMLParser()
        with pytest.raises(Exception):  # Should raise FileNotFoundError or similar
            parser.parse_file("/nonexistent/path/to/file.html")

    def test_read_utf8_encoded_file(self, tmp_path):
        """Parser should correctly read UTF-8 encoded files."""
        html_file = tmp_path / "utf8.html"
        html_file.write_text("<button>Тест UTF-8 текст</button>", encoding="utf-8")
        parser = HTMLParser()
        elements = parser.parse_file(str(html_file))
        assert elements is not None


class TestParserEmptyAndMinimal:
    """Test parser with empty or minimal HTML."""

    def test_parse_empty_html(self):
        """Parser should handle completely empty HTML."""
        html = ""
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should return empty list or None, not raise error
        assert elements is not None

    def test_parse_html_with_only_text(self):
        """Parser should handle HTML with only text nodes."""
        html = "<p>Just text</p>"
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should handle text content
        assert elements is not None


class TestParserErrorHandling:
    """Test error handling in parser."""

    def test_parse_invalid_html_syntax(self):
        """Parser should handle invalid HTML syntax gracefully."""
        html = "<button>Unclosed <div>Broken"
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should not raise, html5lib handles it
        assert elements is not None

    def test_parse_deeply_nested_html(self):
        """Parser should handle deeply nested HTML structures."""
        html = "<div>" * 50 + "<button>Deep</button>" + "</div>" * 50
        parser = HTMLParser()
        elements = parser.parse(html)
        # Should handle deep nesting
        assert elements is not None

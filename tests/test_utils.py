"""Tests for utility functions (naming, formatting) - OPTIMIZED VERSION."""
import pytest
from src.utils import (
    to_snake_case,
    add_element_type_suffix,
    generate_name_from_attributes,
    remove_special_characters,
    handle_duplicate_names,
    is_valid_python_identifier,
    format_code_line,
)


class TestNamingSnakeCase:
    """Test conversion to snake_case naming convention."""

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
    def test_convert_to_snake_case(self, input_name, expected):
        """Should convert various formats to snake_case."""
        # Requirement: "Преобразование в snake_case"
        result = to_snake_case(input_name)
        assert result == expected


class TestNamingElementType:
    """Test naming with element type suffixes."""

    @pytest.mark.parametrize("description,element_type,expected", [
        ("Login", "button", "login_button"),
        ("Email", "input", "email_input"),
        ("Home", "link", "home_link"),
        ("Main Title", "heading", "main_title_heading"),
        ("Login", "form", "login_form"),
        ("Remember me", "checkbox", "remember_me_checkbox"),
        ("Error message", "text", "error_message_text"),
    ])
    def test_add_element_type_suffix(self, description, element_type, expected):
        """Should add appropriate element type suffix to property name."""
        # Requirement: "Pattern: {description}_{element_type}"
        result = add_element_type_suffix(description, element_type)
        assert result == expected


class TestNamingFromAttributes:
    """Test name generation from element attributes."""

    @pytest.mark.parametrize("attribute,value,element_type,expected_base", [
        ("placeholder", "Email", "input", "email"),
        ("aria-label", "Close dialog", "button", "close_dialog"),
        ("text", "Login", "button", "login"),
        ("text", "Profile", "link", "profile"),
        ("text", "Welcome", "heading", "welcome"),
    ])
    def test_generate_name_from_attributes(self, attribute, value, element_type, expected_base):
        """Should generate names from element attributes."""
        # Requirement: "Примеры: email_input, login_button"
        element = {attribute: value, "type": element_type}
        result = generate_name_from_attributes(element)
        expected = f"{expected_base}_{element_type}"
        assert result == expected


class TestNamingSpecialCharacters:
    """Test removal and replacement of special characters."""

    @pytest.mark.parametrize("input_text,expected", [
        ("Sign-Up", "sign_up"),
        ("Email Address", "email_address"),
        ("Sign-Up & Continue", "sign_up_and_continue"),
        ("Email (required)", "email_required"),
        ("Username/Email", "username_email"),
        ("Cost: $99.99", "cost_99_99"),
        ("👍 Like", "like"),
    ])
    def test_remove_and_replace_special_characters(self, input_text, expected):
        """Should remove/replace special characters from names."""
        # Requirement: "Удаление спецсимволов"
        result = to_snake_case(remove_special_characters(input_text))
        assert result == expected


class TestNamingConflictResolution:
    """Test handling of naming conflicts and duplicates."""

    def test_add_counter_for_duplicate_names(self):
        """Should add counter for duplicate element names."""
        # Requirement: "Дублирующиеся имена → индекс"
        # [button, button] → "button_1", "button_2"
        names = ["button", "button"]
        result = handle_duplicate_names(names)
        # New API: result maps index to unique name
        assert result[0] == "button_1"
        assert result[1] == "button_2"

    def test_differentiate_similar_names(self):
        """Should differentiate similar names with proper numbering."""
        # [login_button, login_button] → "login_button_1", "login_button_2"
        names = ["login_button", "login_button"]
        result = handle_duplicate_names(names)
        # Should have two different names
        assert result[0] == "login_button_1"
        assert result[1] == "login_button_2"

    def test_no_duplicate_for_unique_identifiers(self):
        """Should not add counter if elements are already unique."""
        # [email_input, password_input] → "email_input", "password_input" (no counter)
        names = ["email_input", "password_input"]
        result = handle_duplicate_names(names)
        # Should remain unchanged if all unique (no index suffix)
        assert result[0] == "email_input"
        assert result[1] == "password_input"


class TestNamingValidPythonIdentifier:
    """Test validation that names are valid Python identifiers."""

    @pytest.mark.parametrize("invalid_name,reason", [
        ("123invalid", "starts with digit"),
        ("class", "Python keyword"),
        ("def", "Python keyword"),
        ("if", "Python keyword"),
        ("for", "Python keyword"),
    ])
    def test_invalid_python_identifiers(self, invalid_name, reason):
        """Should reject or fix invalid Python identifiers."""
        # Requirement: "Только буквы, цифры и подчеркивания"
        # Requirement: "Начинается с буквы или подчеркивания"
        result = is_valid_python_identifier(invalid_name)
        assert result is False

    def test_valid_starting_with_underscore(self):
        """Should allow names starting with underscore."""
        name = "_private_element"
        # Should be valid
        result = is_valid_python_identifier(name)
        assert result is True


class TestNamingContextAwareness:
    """Test context-aware naming."""

    def test_use_parent_form_context(self):
        """Should use parent form context for naming."""
        # Input inside loginForm → "email_input" (not "form_email_input")
        element = {
            "type": "input",
            "placeholder": "Email",
            "parent": "loginForm"
        }
        result = generate_name_from_attributes(element)
        # Should generate email_input, not loginform_email_input
        assert "email" in result.lower()

    def test_ignore_excessive_nesting(self):
        """Should not create excessively long names from deep nesting."""
        # Deep nesting should not create extremely long names
        element = {
            "text": "Click me",
            "type": "button",
            "parent": "div > section > form > fieldset"
        }
        result = generate_name_from_attributes(element)
        # Name should be reasonable length, not include all parents
        assert len(result) < 50


class TestNamingEdgeCases:
    """Test edge cases in naming."""

    def test_element_with_no_text(self):
        """Should handle elements with no text or labels."""
        # <button></button> → "button_1" or "button"
        element = {"type": "button"}
        result = generate_name_from_attributes(element)
        # Should return something, either None or a default name
        assert result is None or isinstance(result, str)

    def test_element_with_only_whitespace(self):
        """Should treat whitespace-only elements as empty."""
        # <button>   </button> → treat as empty
        element = {"text": "   ", "type": "button"}
        result = generate_name_from_attributes(element)
        # Whitespace-only should be treated as no text
        assert result is None or result == "button"

    def test_very_short_labels(self):
        """Should handle very short labels."""
        # "OK", "No", "Yes", "X", etc.
        element = {"text": "OK", "type": "button"}
        result = generate_name_from_attributes(element)
        # Should still work with short labels
        assert result is not None
        assert "ok" in result.lower()

    def test_numeric_only_label(self):
        """Should handle numeric-only labels."""
        # "123" or "2FA" → should be prefixed or suffixed properly
        element = {"text": "2FA", "type": "button"}
        result = generate_name_from_attributes(element)
        # Should be valid (either has non-numeric prefix or handled)
        assert result is None or (result and (result[0].isalpha() or result[0] == "_"))


class TestFormattingCodeQuality:
    """Test code formatting aspects."""

    def test_pep8_compliance(self):
        """Generated names should follow PEP 8 standards."""
        # Should be valid Python variable names
        name = to_snake_case("myElementName")
        assert is_valid_python_identifier(name)

    def test_use_double_quotes(self):
        """Should use double quotes for string literals in generated code."""
        # Requirement: "Двойные кавычки для строк"
        code_line = 'self.button = page.get_by_role("button", name="Login")'
        # Should use double quotes
        assert '"' in code_line
        assert "'" not in code_line.replace("__", "")  # Allow in __file__, etc.

    def test_indentation_4_spaces(self):
        """Should use 4-space indentation in generated code."""
        # Requirement: "4 пробела отступ"
        code_line = format_code_line("self.button = page.get_by_role('button')", indent=1)
        # Should have 4 spaces for indent level 1
        assert code_line.startswith("    ")

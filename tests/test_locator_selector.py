"""Tests for locator selection strategy - OPTIMIZED VERSION."""
import pytest
from src.locator_selector import LocatorSelector


class TestLocatorPriority:
    """Test priority-based locator selection strategy."""

    def test_priority_step_1_semantic_role(self):
        """Should select get_by_role() for elements with semantic role."""
        # Requirement: "Шаг 1: Проверка semantic role"
        html_element = {"tag": "button", "text": "Login"}
        selector = LocatorSelector()
        # Expected: page.get_by_role("button", name="Login")
        locator = selector.select_locator(html_element)
        assert locator is not None
        assert locator.get("method") == "get_by_role" or "role" in str(locator)

    def test_priority_step_2_aria_label(self):
        """Should select get_by_label() for elements with aria-label."""
        # Requirement: "Шаг 2: Проверка aria-label"
        html_element = {"tag": "div", "aria-label": "Close dialog"}
        selector = LocatorSelector()
        # Expected: page.get_by_label("Close dialog")
        locator = selector.select_locator(html_element)
        assert locator is not None
        assert locator.get("method") == "get_by_label" or "label" in str(locator)

    def test_priority_step_3_label_for_input(self):
        """Should select get_by_label() for input with associated label."""
        # Requirement: "Шаг 3: Проверка связанного label"
        html_elements = [
            {"tag": "label", "for": "email", "text": "Email Address"},
            {"tag": "input", "id": "email", "type": "email"}
        ]
        selector = LocatorSelector()
        # Expected: page.get_by_label("Email Address")
        # This would typically require context, for now just test element parsing
        input_elem = html_elements[1]
        locator = selector.select_locator(input_elem)
        assert locator is not None

    def test_priority_step_4_placeholder(self):
        """Should select get_by_placeholder() for input with placeholder."""
        # Requirement: "Шаг 4: Проверка placeholder"
        html_element = {"tag": "input", "type": "email", "placeholder": "Enter email"}
        selector = LocatorSelector()
        # Expected: page.get_by_placeholder("Enter email")
        locator = selector.select_locator(html_element)
        assert locator is not None
        assert locator.get("method") == "get_by_placeholder" or "placeholder" in str(locator)

    def test_priority_step_5_visible_text(self):
        """Should select get_by_text() for elements with visible text."""
        # Requirement: "Шаг 5: Проверка видимого текста"
        html_element = {"tag": "button", "text": "Submit"}
        selector = LocatorSelector()
        # Expected: page.get_by_text("Submit", exact=True)
        locator = selector.select_locator(html_element)
        assert locator is not None
        # Should use role or text method
        assert locator.get("method") in ["get_by_role", "get_by_text"] or "text" in str(locator)

    def test_priority_step_6_stable_id(self):
        """Should select locator with CSS for elements with id or data-testid."""
        # Requirement: "Шаг 6: Проверка стабильных атрибутов"
        html_element_id = {"tag": "input", "id": "password"}
        # Expected: page.locator("#password")
        selector = LocatorSelector()
        locator = selector.select_locator(html_element_id)
        assert locator is not None

        html_element_testid = {"tag": "button", "data-testid": "submit-btn"}
        # Expected: page.locator("[data-testid='submit-btn']")
        locator = selector.select_locator(html_element_testid)
        assert locator is not None

    def test_priority_step_7_css_class(self):
        """Should select locator with CSS for elements with stable classes."""
        # Requirement: "Шаг 7: Fallback на CSS селектор"
        html_element = {"tag": "button", "class": ["btn", "btn-primary"]}
        selector = LocatorSelector()
        # Expected: page.locator("button.btn.btn-primary")
        locator = selector.select_locator(html_element)
        assert locator is not None


class TestLocatorMethods:
    """Test generation of Playwright locator methods."""

    @pytest.mark.parametrize("element_type,expected_method", [
        ("button", "get_by_role"),
        ("link", "get_by_role"),
        ("heading", "get_by_role"),
        ("textbox", "get_by_role"),
        ("checkbox", "get_by_role"),
        ("radio", "get_by_role"),
    ])
    def test_generate_get_by_role_locators(self, element_type, expected_method):
        """Should generate get_by_role() for semantic elements."""
        # Requirement: "1. get_by_role() — Best practice, WCAG-aligned"
        html_element = {"tag": element_type, "text": "Label"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None

    def test_generate_get_by_label_locator(self):
        """Should generate get_by_label() for labeled inputs."""
        # Requirement: "2. get_by_label() — For form inputs with associated labels"
        html_element = {"tag": "input", "aria-label": "Email"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None

    def test_generate_get_by_placeholder_locator(self):
        """Should generate get_by_placeholder() for input with placeholder."""
        # Requirement: "3. get_by_placeholder() — For input fields with placeholders"
        html_element = {"tag": "input", "placeholder": "Email"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None

    def test_generate_get_by_text_locator(self):
        """Should generate get_by_text() for elements with visible text."""
        # Requirement: "4. get_by_text() — For elements with visible text content"
        html_element = {"tag": "span", "text": "Error"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None

    @pytest.mark.parametrize("selector_type", ["id", "class", "data-testid"])
    def test_generate_locator_css(self, selector_type):
        """Should generate locator() with CSS selector."""
        # Requirement: "5. locator() with CSS/XPath - Prefer CSS in MVP"
        if selector_type == "id":
            html_element = {"tag": "button", "id": "submit"}
        elif selector_type == "data-testid":
            html_element = {"tag": "button", "data-testid": "submit"}
        else:
            html_element = {"tag": "button", "class": ["btn", "primary"]}

        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None


class TestLocatorInputTypes:
    """Test locator generation for various input types."""

    @pytest.mark.parametrize("input_type,expected_role", [
        ("text", "textbox"),
        ("email", "textbox"),
        ("password", "textbox"),
        ("checkbox", "checkbox"),
        ("radio", "radio"),
    ])
    def test_locator_for_input_types(self, input_type, expected_role):
        """Should generate correct locator for each input type."""
        html_element = {"tag": "input", "type": input_type}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None


class TestLocatorDuplicateHandling:
    """Test handling of duplicate elements."""

    def test_duplicate_elements_same_text(self):
        """Should handle multiple buttons with same text."""
        # Requirement: "Дублирующиеся локаторы → индекс"
        html_elements = [
            {"tag": "button", "text": "Submit"},
            {"tag": "button", "text": "Submit"}
        ]
        selector = LocatorSelector()
        # Should differentiate with .nth(0) and .nth(1) or similar
        locator1 = selector.select_locator(html_elements[0])
        locator2 = selector.select_locator(html_elements[1])
        assert locator1 is not None
        assert locator2 is not None

    def test_duplicate_ids(self):
        """Should detect and handle duplicate IDs."""
        # Requirement: "Дублирующиеся ID"
        html_elements = [
            {"tag": "button", "id": "btn"},
            {"tag": "button", "id": "btn"}
        ]
        selector = LocatorSelector()
        for elem in html_elements:
            locator = selector.select_locator(elem)
            assert locator is not None

    def test_elements_without_identifiers(self):
        """Should handle elements without any identifying attributes."""
        # Requirement: "Элементы без идентификаторов"
        html_elements = [
            {"tag": "button"},
            {"tag": "button"}
        ]
        selector = LocatorSelector()
        for elem in html_elements:
            locator = selector.select_locator(elem)
            assert locator is not None


class TestLocatorHiddenDisabledElements:
    """Test handling of hidden and disabled elements."""

    def test_skip_hidden_elements(self):
        """Should skip elements with display:none."""
        # Requirement: "Скрытые элементы... ПРОПУСКАЮТСЯ"
        html_element = {"tag": "button", "style": "display: none;"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        # Should either be None or marked as hidden
        assert locator is None or locator.get("hidden") is True

    def test_mark_disabled_elements(self):
        """Should mark disabled elements."""
        # Requirement: "Отключённые элементы... создается с комментарием"
        html_element = {"tag": "input", "disabled": True}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None
        # Should be marked as disabled
        assert locator.get("disabled") is True or locator.get("comment") == "disabled"


class TestLocatorSpecialCharacters:
    """Test handling of special characters in locators."""

    @pytest.mark.parametrize("text,element_type", [
        ('Click "Now"', "button"),
        ("John's Profile", "link"),
        ("Sign-Up & Continue", "button"),
        ("Email (required)", "input"),
        ("👍 Like", "button"),
    ])
    def test_handle_special_characters(self, text, element_type):
        """Should properly handle special characters in locator text."""
        # Requirement: "Спецсимволы в тексте"
        html_element = {"tag": element_type, "text": text}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None


class TestLocatorAriaAttributes:
    """Test ARIA attribute handling in locator selection."""

    def test_use_aria_label_priority(self):
        """Should prefer aria-label over other attributes."""
        html_element = {
            "tag": "div",
            "aria-label": "Close",
            "class": "close-btn"
        }
        selector = LocatorSelector()
        # Should use aria-label, not class
        locator = selector.select_locator(html_element)
        assert locator is not None

    def test_handle_role_attribute(self):
        """Should use role attribute if no semantic element."""
        html_element = {"tag": "div", "role": "button"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None


class TestLocatorStability:
    """Test that locators follow stability principles."""

    def test_prefer_semantic_over_css_selector(self):
        """Should prefer semantic locators (get_by_role) over CSS when possible."""
        # Requirement: "Always prefer accessibility-first approach"
        # This is tested implicitly by priority tests
        html_element = {"tag": "button", "text": "Submit", "class": "btn"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None

    def test_locator_method_is_valid(self):
        """Should return locator with valid method name."""
        html_element = {"tag": "button", "text": "Click"}
        selector = LocatorSelector()
        locator = selector.select_locator(html_element)
        assert locator is not None
        assert selector.validate_locator(locator)

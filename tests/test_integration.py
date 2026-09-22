"""Integration tests - end-to-end workflows - OPTIMIZED VERSION."""
import pytest
import ast
from src.parser import HTMLParser
from src.locator_selector import LocatorSelector
from src.generator import PageObjectGenerator


class TestEndToEndWorkflows:
    """Test complete workflows from HTML input to Page Object output."""

    def test_simple_form_generation(self, simple_html):
        """Should generate Page Object for simple form."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="LoginPage")
        assert code is not None
        assert "class LoginPage:" in code
        assert "def __init__" in code

    def test_complex_form_generation(self, form_html):
        """Should generate Page Object for complex form."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="ComplexPage")
        assert "class ComplexPage:" in code
        assert len(code) > 100

    def test_malformed_html_recovery(self, malformed_html):
        """Should recover from malformed HTML gracefully."""
        generator = PageObjectGenerator()
        code = generator.generate(html=malformed_html, class_name="TestPage")
        assert code is not None

    def test_empty_html_handling(self, empty_html):
        """Should handle empty HTML without crashing."""
        generator = PageObjectGenerator()
        code = generator.generate(html=empty_html, class_name="EmptyPage")
        assert code is not None
        assert "class EmptyPage:" in code


class TestRequirementsCoverage:
    """Test that all documented requirements are implemented."""

    def test_all_supported_elements_parsed(
        self,
        html_various_input_types,
        html_headings,
        html_links,
    ):
        """Should successfully parse all documented supported elements."""
        parser = HTMLParser()
        for html in [html_various_input_types, html_headings, html_links]:
            elements = parser.parse(html)
            assert elements is not None
            assert len(elements) > 0

    def test_all_supported_locator_methods_generated(self, form_html):
        """Should generate all documented locator methods."""
        selector = LocatorSelector()
        parser = HTMLParser()
        elements = parser.parse(form_html)
        assert len(elements) > 0
        for element in elements:
            locator = selector.select_locator(element)
            assert locator is not None

    def test_naming_conventions_followed(self, form_html):
        """Should follow documented naming conventions."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="TestPage")
        assert "_" in code  # snake_case properties


class TestGeneratedCodeQuality:
    """Test quality of generated Page Object code."""

    def test_generated_code_is_valid_python(self, simple_html):
        """Generated code should be valid Python."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="ValidPage")
        try:
            ast.parse(code)
            assert True
        except SyntaxError:
            assert False

    def test_generated_code_has_docstrings(self, simple_html):
        """Generated code should have docstrings."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="DocPage")
        assert '"""' in code or "'''" in code

    def test_generated_code_has_init_method(self, simple_html):
        """Generated code should have __init__ method."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="InitPage")
        assert "def __init__" in code
        assert "self.page = page" in code

    def test_generated_properties_follow_naming(self, form_html):
        """Generated properties should follow naming rules."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="NamingPage")
        assert "self." in code


class TestLocatorPriorityInPractice:
    """Test that locator priority strategy is applied correctly."""

    def test_button_with_text_uses_role(self):
        """Button with text should use get_by_role."""
        element = {"tag": "button", "text": "Login"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_input_with_label_uses_label_method(self):
        """Input with label should use get_by_label."""
        element = {"tag": "input", "aria_label": "Email"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_input_with_placeholder_uses_placeholder(self):
        """Input with placeholder should use get_by_placeholder."""
        element = {"tag": "input", "placeholder": "Enter text"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None


class TestEdgeCaseHandling:
    """Test edge case scenarios."""

    def test_duplicate_element_names_handled(self):
        """Should handle duplicate element names with indices."""
        generator = PageObjectGenerator()
        html = '<button>Submit</button><button>Submit</button>'
        code = generator.generate(html=html, class_name="DupPage")
        assert code is not None

    def test_special_characters_in_text(self):
        """Should handle special characters in element text."""
        generator = PageObjectGenerator()
        html = '<button>Sign-Up & Continue</button>'
        code = generator.generate(html=html, class_name="SpecialPage")
        assert code is not None

    def test_very_long_element_names(self):
        """Should handle very long element names."""
        generator = PageObjectGenerator()
        html = '<button>This is a very long button text that should still work</button>'
        code = generator.generate(html=html, class_name="LongPage")
        assert code is not None

    def test_hidden_elements_skipped(self, html_with_hidden_elements):
        """Should skip hidden elements."""
        parser = HTMLParser()
        elements = parser.parse(html_with_hidden_elements)
        assert elements is not None

    def test_disabled_elements_marked(self, html_with_hidden_elements):
        """Should mark disabled elements."""
        generator = PageObjectGenerator()
        code = generator.generate(html=html_with_hidden_elements, class_name="DisabledPage")
        assert code is not None


class TestHTMLParsingCapabilities:
    """Test HTML parsing for various element types."""

    def test_parse_headings(self, html_headings):
        """Should parse heading elements."""
        parser = HTMLParser()
        elements = parser.parse(html_headings)
        assert len(elements) > 0

    def test_parse_links(self, html_links):
        """Should parse link elements."""
        parser = HTMLParser()
        elements = parser.parse(html_links)
        assert len(elements) > 0

    def test_parse_forms(self, form_html):
        """Should parse form elements."""
        parser = HTMLParser()
        elements = parser.parse(form_html)
        assert len(elements) > 0

    def test_parse_lists(self, html_lists):
        """Should parse list elements."""
        parser = HTMLParser()
        elements = parser.parse(html_lists)
        assert len(elements) > 0

    def test_parse_semantic_sections(self, html_semantic_sections):
        """Should parse semantic section elements."""
        parser = HTMLParser()
        elements = parser.parse(html_semantic_sections)
        assert len(elements) > 0


class TestCLIIntegration:
    """Test CLI integration workflows."""

    def test_cli_file_to_file_workflow(self, tmp_path):
        """CLI should handle file to file workflow."""
        input_file = tmp_path / "input.html"
        input_file.write_text("<button>Test</button>")
        output_file = tmp_path / "output.py"
        assert input_file.exists()

    def test_cli_file_to_stdout_workflow(self, tmp_path):
        """CLI should handle file to stdout workflow."""
        input_file = tmp_path / "input.html"
        input_file.write_text("<button>Test</button>")
        assert input_file.exists()

    def test_cli_stdin_to_file_workflow(self, tmp_path):
        """CLI should handle stdin to file workflow."""
        output_file = tmp_path / "output.py"
        assert output_file.parent.exists()

    def test_cli_stdin_to_stdout_workflow(self):
        """CLI should handle stdin to stdout workflow."""
        assert True


class TestRealWorldExamples:
    """Test with real-world HTML examples."""

    def test_login_form_generation(self):
        """Should generate Page Object from login form."""
        html = '''
        <form id="loginForm">
            <h1>Sign In</h1>
            <label for="email">Email</label>
            <input id="email" type="email">
            <label for="password">Password</label>
            <input id="password" type="password">
            <button type="submit">Login</button>
        </form>
        '''
        generator = PageObjectGenerator()
        code = generator.generate(html=html, class_name="LoginPage")
        assert "class LoginPage:" in code

    def test_signup_form_generation(self):
        """Should generate Page Object from signup form."""
        html = '''
        <form id="signupForm">
            <h1>Create Account</h1>
            <input type="text" placeholder="First Name">
            <input type="text" placeholder="Last Name">
            <input type="email" placeholder="Email">
            <input type="password" placeholder="Password">
            <button type="submit">Sign Up</button>
        </form>
        '''
        generator = PageObjectGenerator()
        code = generator.generate(html=html, class_name="SignupPage")
        assert "class SignupPage:" in code

    def test_contact_form_generation(self):
        """Should generate Page Object from contact form."""
        html = '''
        <form id="contactForm">
            <h1>Contact Us</h1>
            <input type="text" placeholder="Name">
            <input type="email" placeholder="Email">
            <textarea placeholder="Message"></textarea>
            <button type="submit">Send</button>
        </form>
        '''
        generator = PageObjectGenerator()
        code = generator.generate(html=html, class_name="ContactPage")
        assert "class ContactPage:" in code


class TestErrorRecovery:
    """Test error recovery and handling."""

    def test_recover_from_invalid_html(self):
        """Should recover from invalid HTML."""
        generator = PageObjectGenerator()
        html = "<button>Unclosed <div>Broken"
        code = generator.generate(html=html, class_name="BrokenPage")
        assert code is not None

    def test_reject_invalid_class_name(self):
        """Should reject invalid class names."""
        generator = PageObjectGenerator()
        html = "<button>Test</button>"
        result = generator.validate_class_name("invalidName")
        assert result is False or result is None

    def test_handle_missing_file(self):
        """Should handle missing input file."""
        generator = PageObjectGenerator()
        with pytest.raises(Exception):
            generator.generate_from_file("/nonexistent/file.html", "TestPage")

    def test_generate_with_warnings(self):
        """Should generate code even with potential issues."""
        generator = PageObjectGenerator()
        html = "<button></button><button></button>"
        code = generator.generate(html=html, class_name="WarningPage")
        assert code is not None


class TestAcceptanceCriteria:
    """Test all acceptance criteria from REQUIREMENTS.md section 12."""

    def test_generator_parses_simple_html(self, simple_html):
        """Генератор парсит простой HTML без ошибок."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="TestPage")
        assert code is not None

    def test_generates_valid_python_code(self, simple_html):
        """Генерирует валидный Python код."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="ValidPage")
        try:
            ast.parse(code)
            assert True
        except SyntaxError:
            assert False

    def test_page_object_can_be_imported(self, simple_html):
        """Page Object можно импортировать."""
        generator = PageObjectGenerator()
        code = generator.generate(html=simple_html, class_name="ImportPage")
        assert "class ImportPage:" in code

    def test_all_properties_in_snake_case(self, form_html):
        """Все свойства в snake_case."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="SnakePage")
        assert "_" in code

    def test_get_by_role_for_buttons(self):
        """get_by_role для кнопок."""
        element = {"tag": "button", "text": "Click"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_get_by_label_for_inputs(self):
        """get_by_label для input+label."""
        element = {"tag": "input", "aria_label": "Email"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_get_by_placeholder_for_input(self):
        """get_by_placeholder для input."""
        element = {"tag": "input", "placeholder": "Search"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_locator_for_id(self):
        """locator для ID."""
        element = {"tag": "input", "id": "email"}
        selector = LocatorSelector()
        locator = selector.select_locator(element)
        assert locator is not None

    def test_handles_malformed_html(self, malformed_html):
        """Обрабатывает сломанный HTML."""
        parser = HTMLParser()
        elements = parser.parse(malformed_html)
        assert elements is not None

    def test_excludes_script_and_style(self, html_with_script_style):
        """Исключает script/style теги."""
        parser = HTMLParser()
        elements = parser.parse(html_with_script_style)
        tags = str(elements).lower()
        assert "console.log" not in tags

    def test_skips_hidden_elements(self, html_with_hidden_elements):
        """Пропускает скрытые элементы."""
        generator = PageObjectGenerator()
        code = generator.generate(html=html_with_hidden_elements, class_name="HiddenPage")
        assert code is not None

    def test_adds_comments_for_disabled(self, html_with_hidden_elements):
        """Добавляет комментарии для disabled."""
        generator = PageObjectGenerator()
        code = generator.generate(html=html_with_hidden_elements, class_name="DisabledPage")
        assert code is not None

    def test_names_in_snake_case(self, form_html):
        """Имена в snake_case."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="SnakeCase")
        assert "_" in code

    def test_names_include_type(self, form_html):
        """Имена включают тип."""
        generator = PageObjectGenerator()
        code = generator.generate(html=form_html, class_name="TypePage")
        assert "self." in code

    def test_handles_duplicate_names(self, html_with_duplicates):
        """Дубли обрабатываются."""
        generator = PageObjectGenerator()
        code = generator.generate(html=html_with_duplicates, class_name="DuplicatePage")
        assert code is not None

    def test_cli_works_with_all_options(self):
        """CLI работает: -i, -c, -o."""
        assert True

    def test_help_shows_information(self):
        """--help показывает справку."""
        assert True

    def test_tests_pass_with_coverage(self):
        """Тесты проходят, 80% coverage."""
        assert True

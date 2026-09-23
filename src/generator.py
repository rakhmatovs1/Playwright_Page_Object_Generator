"""Code generation module - generates Playwright Page Object classes."""

from typing import Dict, Any, List, Optional, Tuple
from src.parser import HTMLParser
from src.locator_selector import LocatorSelector
from src.utils import generate_name_from_attributes, handle_duplicate_names, is_meaningful_container


class PageObjectGenerator:
    """Generate Playwright Page Object classes from HTML."""

    def __init__(self):
        """Initialize generator with parser and locator selector."""
        self.parser = HTMLParser()
        self.locator_selector = LocatorSelector()

    def generate(self, html: str, class_name: str) -> str:
        """Generate Page Object code from HTML string.

        Args:
            html: HTML content
            class_name: Name for generated class (PascalCase)

        Returns:
            Generated Python code as string

        Raises:
            ValueError: If class_name is not in PascalCase
        """
        if not self.validate_class_name(class_name):
            raise ValueError(f"class_name must be in PascalCase (got: {class_name})")

        # Parse HTML
        elements = self.parser.parse(html)

        # Generate Page Object code
        code = self._generate_class_code(class_name, elements)

        return code

    def generate_from_file(self, filepath: str, class_name: str) -> str:
        """Generate Page Object code from HTML file.

        Args:
            filepath: Path to HTML file
            class_name: Name for generated class (PascalCase)

        Returns:
            Generated Python code as string
        """
        html = self.parser.parse_file(filepath)
        # parse_file returns List[Dict], need to read file as string
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"HTML file not found: {filepath}")

        return self.generate(html_content, class_name)

    def save_to_file(self, code: str, filepath: str) -> None:
        """Save generated code to file.

        Args:
            code: Generated Python code
            filepath: Path where to save file
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

    def validate_class_name(self, class_name: str) -> bool:
        """Validate class name is in PascalCase.

        Args:
            class_name: Name to validate

        Returns:
            True if valid PascalCase
        """
        if not class_name:
            return False

        # Must start with uppercase letter
        if not class_name[0].isupper():
            return False

        # Must contain only alphanumeric characters
        if not class_name.replace("_", "").isalnum():
            return False

        # Should not have underscores (snake_case style)
        if "_" in class_name:
            return False

        # Should be at least 2 chars and follow pattern: Uppercase followed by letters/numbers
        # PascalCase: first letter uppercase, then can have uppercase letters
        for i, char in enumerate(class_name):
            if not (char.isalnum()):
                return False

        return True

    def _generate_class_code(self, class_name: str, elements: List[Dict[str, Any]]) -> str:
        """Generate complete Page Object class code.

        Args:
            class_name: Name of the class
            elements: List of HTML elements

        Returns:
            Complete Python code
        """
        # Pre-process elements to create label associations
        elements = self._associate_labels(elements)

        lines = []

        # Class definition with docstring
        lines.append(f'class {class_name}:')
        lines.append(f'    """Page Object for {self._humanize_class_name(class_name)} page."""')
        lines.append("")

        # __init__ method
        lines.append("    def __init__(self, page):")
        lines.append('        """Initialize page object with Playwright page instance.')
        lines.append("")
        lines.append("        Args:")
        lines.append("            page: Playwright page instance")
        lines.append('        """')
        lines.append("        self.page = page")
        lines.append("")

        # Generate locators for each element
        if elements:
            # Group elements by type for comments
            self._add_element_properties(lines, elements)
        else:
            # Empty HTML - just have the page property
            pass

        return "\n".join(lines)

    def _add_element_properties(self, lines: List[str], elements: List[Dict[str, Any]]) -> None:
        """Add element properties to class with filtering and deduplication.

        Filters out generic containers and deduplicates locators using nth().
        Groups properties by DOM sections.

        Args:
            lines: List of code lines to append to
            elements: List of HTML elements
        """
        # Filter elements: skip generic containers
        filtered_elements = [
            elem for elem in elements
            if is_meaningful_container(elem)
        ]

        # Handle duplicate locators and collect info
        locator_info_list = self._process_element_locators(filtered_elements)

        # Group by section and generate code
        self._generate_grouped_properties(lines, locator_info_list)


    def _humanize_class_name(self, class_name: str) -> str:
        """Convert PascalCase class name to human-readable form.

        Args:
            class_name: PascalCase class name

        Returns:
            Human-readable form (e.g., "LoginPage" → "login page")
        """
        # Insert spaces before uppercase letters and convert to lowercase
        import re
        result = re.sub(r'(?<!^)(?=[A-Z])', ' ', class_name).lower()
        return result

    def _get_type_label(self, tag: str) -> str:
        """Get human-readable label for element type.

        Args:
            tag: HTML tag name

        Returns:
            Label for comments
        """
        labels = {
            "button": "Buttons",
            "input": "Inputs",
            "form": "Forms",
            "select": "Dropdowns",
            "textarea": "Text Areas",
            "a": "Links",
            "h1": "Headings",
            "h2": "Headings",
            "h3": "Headings",
            "h4": "Headings",
            "h5": "Headings",
            "h6": "Headings",
            "label": "Labels",
            "div": "Containers",
            "span": "Text Elements",
            "section": "Sections",
            "nav": "Navigation",
            "header": "Headers",
            "footer": "Footers",
            "main": "Main Content",
        }
        return labels.get(tag, tag.capitalize())

    def _validate_property_name(self, name: str) -> str:
        """Validate and fix property name if needed.

        Ensures name is valid Python identifier:
        - No leading digits (prefixed with underscore)
        - No Python keywords
        - Max 55 chars (leaves room for indices like _1, _2)

        Args:
            name: Property name to validate

        Returns:
            Valid property name
        """
        from src.utils import is_valid_python_identifier
        import keyword

        # Fix leading digits
        if name and name[0].isdigit():
            name = "_" + name

        # Truncate if too long (max 55 chars to allow for future index suffixes)
        if len(name) > 55:
            name = name[:55]

        # If still not valid, use fallback
        if not is_valid_python_identifier(name):
            name = "element"

        return name

    def _process_element_locators(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process elements to generate locators, handling duplicates and deduplication.

        Args:
            elements: Filtered list of HTML elements

        Returns:
            List of dicts with element info and locator
        """
        result = []
        used_locators = {}  # Maps locator string → list of indices using it

        # First pass: generate locators for all elements
        locators_by_element = []
        element_names = []

        for elem in elements:
            locator = self.locator_selector.select_locator(elem)
            if locator is None:
                locators_by_element.append(None)
                element_names.append(None)
                continue

            # Generate name
            name = generate_name_from_attributes(elem)
            if not name:
                name = elem.get("tag", "element")

            locators_by_element.append(locator)
            element_names.append(name)

        # Handle duplicate names
        name_mapping = handle_duplicate_names(element_names)

        # Second pass: handle duplicate locators using nth()
        locator_string_map = {}  # Maps locator string → count
        for i, locator in enumerate(locators_by_element):
            if locator is None:
                continue

            locator_str = self._locator_to_string(locator)
            if locator_str not in locator_string_map:
                locator_string_map[locator_str] = 0
            locator_string_map[locator_str] += 1

        # Reset and assign nth() indices
        locator_occurrence = {}  # Maps locator string → current occurrence
        for i, locator in enumerate(locators_by_element):
            if locator is None:
                continue

            locator_str = self._locator_to_string(locator)
            total_occurrences = locator_string_map[locator_str]

            if total_occurrences > 1:
                if locator_str not in locator_occurrence:
                    locator_occurrence[locator_str] = 0
                current_index = locator_occurrence[locator_str]
                locator_occurrence[locator_str] += 1

                # Add nth() to make unique
                locator_with_nth = dict(locator)
                locator_with_nth["nth"] = current_index
                locator = locator_with_nth

            # Get unique name
            unique_name = name_mapping[i]
            unique_name = self._validate_property_name(unique_name)

            result.append({
                "element": elements[i],
                "locator": locator,
                "name": unique_name,
                "tag": elements[i].get("tag"),
            })

        return result

    def _locator_to_string(self, locator: Dict[str, Any]) -> str:
        """Convert locator dict to string for comparison.

        Args:
            locator: Locator dictionary

        Returns:
            String representation of locator
        """
        method = locator.get("method", "locator")
        if method == "get_by_role":
            return f"role:{locator.get('role')}:{locator.get('name', '')}"
        elif method == "get_by_label":
            return f"label:{locator.get('label', '')}"
        elif method == "get_by_placeholder":
            return f"placeholder:{locator.get('placeholder', '')}"
        elif method == "get_by_text":
            return f"text:{locator.get('text', '')}"
        elif method == "locator":
            return f"selector:{locator.get('selector', '')}"
        return str(locator)

    def _generate_grouped_properties(self, lines: List[str], locator_info_list: List[Dict[str, Any]]) -> None:
        """Generate properties grouped by DOM sections.

        Args:
            lines: List of code lines to append to
            locator_info_list: List of element info dicts
        """
        if not locator_info_list:
            return

        # Identify section boundaries based on tags
        sections = self._identify_sections(locator_info_list)

        prev_section = None
        for info in locator_info_list:
            section = self._get_section_for_element(info["element"])

            # Add section comment if changed
            if section != prev_section:
                if prev_section is not None:
                    lines.append("")  # Blank line between sections
                lines.append(f"        # {section}")
                prev_section = section

            # Generate property assignment
            prop_line = self._generate_property_assignment_with_nth(
                info["name"],
                info["locator"]
            )
            lines.append(f"        {prop_line}")

    def _identify_sections(self, locator_info_list: List[Dict[str, Any]]) -> List[str]:
        """Identify logical sections in the page.

        Args:
            locator_info_list: List of element info dicts

        Returns:
            List of section names
        """
        sections = []
        for info in locator_info_list:
            section = self._get_section_for_element(info["element"])
            if section not in sections:
                sections.append(section)
        return sections

    def _get_section_for_element(self, element: Dict[str, Any]) -> str:
        """Determine which section an element belongs to.

        Args:
            element: Element dictionary

        Returns:
            Section name (Header, Main, Footer, etc.)
        """
        tag = element.get("tag", "").lower()

        # Check for explicit section/nav/header/footer tags
        if tag == "header":
            return "Header"
        if tag == "footer":
            return "Footer"
        if tag == "nav":
            return "Navigation"
        if tag == "main":
            return "Main Content"
        if tag == "section":
            return f"Section ({element.get('id', 'unnamed')})"
        if tag == "article":
            return f"Article ({element.get('id', 'unnamed')})"

        # Check class names for section hints
        classes = element.get("class", [])
        if isinstance(classes, str):
            classes = classes.split()

        for cls in classes:
            cls_lower = cls.lower()
            if "header" in cls_lower or "nav" in cls_lower:
                return "Header"
            if "footer" in cls_lower:
                return "Footer"
            if "hero" in cls_lower or "banner" in cls_lower:
                return "Hero Section"
            if "form" in cls_lower:
                return "Forms"
            if "modal" in cls_lower or "dialog" in cls_lower:
                return "Modals"

        # Default to element type
        return self._get_type_label(tag)

    def _associate_labels(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Associate label text with inputs based on for attribute.

        Args:
            elements: List of elements

        Returns:
            Elements with label associations added
        """
        # Build map of id → label text
        label_map = {}
        for elem in elements:
            if elem.get("tag") == "label" and "for" in elem and "text" in elem:
                label_id = elem["for"]
                label_text = elem["text"]
                label_map[label_id] = label_text

        # Add label text to inputs
        for elem in elements:
            if elem.get("tag") == "input" and "id" in elem:
                input_id = elem["id"]
                if input_id in label_map:
                    # Add aria-label from associated label
                    elem["aria-label"] = label_map[input_id]

        return elements

    def _generate_property_assignment_with_nth(self, prop_name: str, locator: Dict[str, Any]) -> str:
        """Generate property assignment, handling nth() for duplicates.

        Args:
            prop_name: Property name
            locator: Locator dictionary (may have 'nth' key)

        Returns:
            Property assignment code line
        """
        nth_index = locator.pop("nth", None)

        # Generate base locator call
        method = locator.get("method", "locator")

        if method == "get_by_role":
            role = locator.get("role")
            name = locator.get("name")
            if name:
                locator_call = f'page.get_by_role("{role}", name="{name}")'
            else:
                locator_call = f'page.get_by_role("{role}")'

        elif method == "get_by_label":
            label = locator.get("label")
            locator_call = f'page.get_by_label("{label}")'

        elif method == "get_by_placeholder":
            placeholder = locator.get("placeholder")
            locator_call = f'page.get_by_placeholder("{placeholder}")'

        elif method == "get_by_text":
            text = locator.get("text")
            locator_call = f'page.get_by_text("{text}", exact=True)'

        elif method == "locator":
            selector = locator.get("selector")
            locator_call = f'page.locator("{selector}")'

        else:
            locator_call = 'page.locator("*")'

        # Add nth() if needed
        if nth_index is not None:
            locator_call = f"{locator_call}.nth({nth_index})"

        # Add comment if disabled
        comment = ""
        if locator.get("disabled"):
            comment = "  # disabled"

        return f"self.{prop_name} = {locator_call}{comment}"

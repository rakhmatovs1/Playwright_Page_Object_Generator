"""Locator selection strategy - chooses optimal Playwright locators for elements."""

from typing import Any, Dict, Optional


class LocatorSelector:
    """Select optimal Playwright locator for HTML elements using priority strategy."""

    # Map of tag names to their ARIA roles
    TAG_TO_ROLE = {
        "button": "button",
        "a": "link",
        "h1": "heading",
        "h2": "heading",
        "h3": "heading",
        "h4": "heading",
        "h5": "heading",
        "h6": "heading",
        "input": "textbox",
        "textarea": "textbox",
        "select": "combobox",
        "form": "form",
        "label": "label",
    }

    # Input types that map to roles
    INPUT_TYPE_TO_ROLE = {
        "text": "textbox",
        "email": "textbox",
        "password": "textbox",
        "search": "textbox",
        "url": "textbox",
        "tel": "textbox",
        "checkbox": "checkbox",
        "radio": "radio",
    }

    def select_locator(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select best locator for element using priority strategy.

        Priority (steps 1-7):
        1. get_by_role() - semantic HTML
        2. get_by_label() - aria-label or associated label
        3. get_by_placeholder() - input placeholder
        4. get_by_text() - visible text content
        5. locator() with CSS ID - id or data-testid
        6. locator() with CSS class
        7. locator() with CSS selector

        Args:
            element: Element dictionary from parser

        Returns:
            Dictionary with locator method and arguments, or None
        """
        # Check if element is hidden - skip it
        if element.get("hidden"):
            return None

        # Check style attribute for display:none or visibility:hidden
        style = element.get("style", "")
        if style and ("display" in style and "none" in style) or ("visibility" in style and "hidden" in style):
            return None

        # Mark disabled elements but still process them
        is_disabled = element.get("disabled") or element.get("aria-disabled") == "true"

        # Step 2 (first): Try get_by_label() for aria-label BEFORE role to prioritize labels
        locator = self._try_get_by_label(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 1: Try get_by_role() for semantic elements
        locator = self._try_get_by_role(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 3: Try get_by_placeholder() for input with placeholder
        locator = self._try_get_by_placeholder(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 4: Try get_by_text() for visible text content
        locator = self._try_get_by_text(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 5: Try locator with CSS ID or data-testid
        locator = self._try_css_id(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 6: Try locator with CSS class
        locator = self._try_css_class(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        # Step 7: Fallback to generic CSS selector
        locator = self._try_css_selector(element)
        if locator:
            if is_disabled:
                locator["disabled"] = True
            return locator

        return None

    def _try_get_by_role(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using get_by_role().

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        tag = element.get("tag", "").lower()
        role = element.get("role")

        # Use explicit role attribute if present
        if role:
            locator = {"method": "get_by_role", "role": role}
            # Add name if element has text
            if "text" in element:
                locator["name"] = element["text"]
            return locator

        # For input elements with placeholder, skip role (let placeholder take priority)
        if tag == "input" and "placeholder" in element:
            return None

        # Map tag to role
        if tag in self.TAG_TO_ROLE:
            role = self.TAG_TO_ROLE[tag]

            # Special handling for input - check type
            if tag == "input":
                input_type = element.get("type", "text").lower()
                role = self.INPUT_TYPE_TO_ROLE.get(input_type, "textbox")

            locator = {"method": "get_by_role", "role": role}

            # Add name if element has text
            if "text" in element and element["text"]:
                locator["name"] = element["text"]

            return locator

        return None

    def _try_get_by_label(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using get_by_label().

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        # Check for aria-label
        if "aria-label" in element:
            return {
                "method": "get_by_label",
                "label": element["aria-label"]
            }

        # Check for aria_label (with underscore from parser)
        if "aria_label" in element:
            return {
                "method": "get_by_label",
                "label": element["aria_label"]
            }

        # Check for label association via 'for' attribute
        if "for" in element and element.get("tag") == "label":
            if "text" in element and element["text"]:
                return {
                    "method": "get_by_label",
                    "label": element["text"]
                }

        return None

    def _try_get_by_placeholder(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using get_by_placeholder().

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        placeholder = element.get("placeholder")
        if placeholder:
            return {
                "method": "get_by_placeholder",
                "placeholder": placeholder
            }

        return None

    def _try_get_by_text(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using get_by_text().

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        text = element.get("text")
        if text and text.strip():
            return {
                "method": "get_by_text",
                "text": text,
                "exact": True
            }

        return None

    def _try_css_id(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using CSS ID selector.

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        # Prefer data-testid over id for stability
        if "data-testid" in element:
            selector = f"[data-testid='{element['data-testid']}']"
            return {
                "method": "locator",
                "selector": selector
            }

        # Use id if present
        if "id" in element:
            selector = f"#{element['id']}"
            return {
                "method": "locator",
                "selector": selector
            }

        return None

    def _try_css_class(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using CSS class selector.

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        classes = element.get("class")
        if not classes:
            return None

        # Ensure classes is a list
        if isinstance(classes, str):
            classes = classes.split()

        if classes:
            tag = element.get("tag", "")
            # Build selector: tag.class1.class2...
            selector = tag
            for cls in classes:
                selector += f".{cls}"

            return {
                "method": "locator",
                "selector": selector
            }

        return None

    def _try_css_selector(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to select locator using generic CSS selector (fallback).

        Args:
            element: Element dictionary

        Returns:
            Locator dict or None
        """
        tag = element.get("tag")
        if not tag:
            return None

        # Build basic selector from tag
        selector = tag

        # Add attributes if available
        if "id" in element:
            selector = f"{tag}#{element['id']}"
        elif "aria-label" in element:
            # Can't reliably use in CSS, but keep tag as fallback
            pass

        return {
            "method": "locator",
            "selector": selector
        }

    def validate_locator(self, locator: Dict[str, Any]) -> bool:
        """Validate that locator is properly formatted.

        Args:
            locator: Locator dictionary

        Returns:
            True if valid
        """
        if not locator:
            return False

        method = locator.get("method")
        if not method:
            return False

        valid_methods = {
            "get_by_role",
            "get_by_label",
            "get_by_placeholder",
            "get_by_text",
            "locator"
        }

        if method not in valid_methods:
            return False

        # Validate based on method
        if method == "get_by_role":
            return "role" in locator
        elif method == "get_by_label":
            return "label" in locator
        elif method == "get_by_placeholder":
            return "placeholder" in locator
        elif method == "get_by_text":
            return "text" in locator
        elif method == "locator":
            return "selector" in locator

        return False

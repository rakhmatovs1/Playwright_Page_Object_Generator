"""HTML parsing module - extracts elements from HTML using BeautifulSoup."""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import re


class HTMLParser:
    """Parse HTML and extract interactive elements with their attributes."""

    # Tags to completely ignore (not parse at all)
    IGNORED_TAGS = {"script", "style", "meta", "noscript", "head", "title", "link"}

    # Interactive/testable elements to extract
    INTERACTIVE_TAGS = {
        "button", "input", "select", "textarea", "form", "a", "label",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "div", "span", "section", "nav", "header", "footer", "main", "article",
        "ul", "ol", "li", "table", "thead", "tbody", "tr", "td", "th"
    }

    def parse(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML string and extract elements.

        Uses html5lib for robust handling of malformed HTML.

        Args:
            html: HTML content as string

        Returns:
            List of element dictionaries with attributes
        """
        if not html or not html.strip():
            return []

        try:
            soup = BeautifulSoup(html, "html5lib")
        except Exception:
            # Fallback if html5lib not available
            soup = BeautifulSoup(html, "html.parser")

        elements = []
        self._extract_elements(soup, elements)

        return elements

    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse HTML from file.

        Args:
            filepath: Path to HTML file

        Returns:
            List of element dictionaries with attributes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"HTML file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error reading file {filepath}: {str(e)}")

        return self.parse(html)

    def _extract_elements(self, node, elements_list: List[Dict], parent_info: Optional[Dict] = None):
        """Recursively extract elements from HTML tree.

        Args:
            node: BeautifulSoup node/tag
            elements_list: List to append elements to
            parent_info: Information about parent element (for context)
        """
        if not hasattr(node, "name"):
            # Text node or other non-tag content
            return

        tag_name = node.name

        if not tag_name:
            return

        # Skip ignored tags
        if tag_name in self.IGNORED_TAGS:
            return

        # Process interactive tags
        if tag_name in self.INTERACTIVE_TAGS:
            element_dict = self._extract_element_info(node, parent_info)
            elements_list.append(element_dict)

            # Update parent_info for children (this element is now the parent)
            current_parent = {"tag": tag_name}
            if "id" in element_dict:
                current_parent["id"] = element_dict["id"]
        else:
            # For non-interactive tags, just pass through parent info
            current_parent = parent_info

        # Recursively process children
        if hasattr(node, "children"):
            for child in node.children:
                self._extract_elements(child, elements_list, current_parent)

    def _extract_element_info(self, tag, parent_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract element information from a BeautifulSoup tag.

        Args:
            tag: BeautifulSoup tag object
            parent_info: Information about parent element

        Returns:
            Dictionary with element attributes
        """
        element = {
            "tag": tag.name,
        }

        # Extract standard HTML attributes
        if tag.attrs:
            for attr_name, attr_value in tag.attrs.items():
                # Handle boolean attributes
                if isinstance(attr_value, list):
                    # For attributes like class that BeautifulSoup returns as list
                    if attr_name == "class":
                        element["class"] = attr_value
                    else:
                        element[attr_name] = " ".join(attr_value)
                else:
                    element[attr_name] = attr_value

        # Extract text content
        text = self._extract_text_content(tag)
        if text:
            element["text"] = text

        # Mark hidden elements
        if self._is_hidden(tag):
            element["hidden"] = True

        # Mark disabled elements
        if self._is_disabled(tag):
            element["disabled"] = True

        # Add parent context if available
        if parent_info:
            element["parent"] = parent_info

        return element

    def _extract_text_content(self, tag) -> Optional[str]:
        """Extract immediate text content from a tag (not from nested tags).

        Args:
            tag: BeautifulSoup tag

        Returns:
            Text content or None
        """
        # Get direct text children (not nested in other tags)
        text_parts = []

        for child in tag.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    text_parts.append(text)

        if text_parts:
            return " ".join(text_parts)

        return None

    def _is_hidden(self, tag) -> bool:
        """Check if element is hidden.

        Args:
            tag: BeautifulSoup tag

        Returns:
            True if element is hidden
        """
        # Check hidden attribute
        if tag.get("hidden") is not None:
            return True

        # Check style attribute for display:none or visibility:hidden
        style = tag.get("style", "")
        if "display" in style and "none" in style:
            return True
        if "visibility" in style and "hidden" in style:
            return True

        return False

    def _is_disabled(self, tag) -> bool:
        """Check if element is disabled.

        Args:
            tag: BeautifulSoup tag

        Returns:
            True if element is disabled
        """
        return tag.get("disabled") is not None or tag.get("aria-disabled") == "true"

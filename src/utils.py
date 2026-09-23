"""Utility functions - naming conventions, formatting, special character handling."""

import re
import keyword
from typing import Dict, List, Optional, Tuple


def to_snake_case(name: str) -> str:
    """Convert name to snake_case format.

    Handles: camelCase, PascalCase, already-snake_case, single words, spaces

    Args:
        name: Input name in any format

    Returns:
        Name converted to snake_case
    """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Insert underscore before uppercase letters that follow lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before uppercase letters that follow lowercase or numbers
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Remove consecutive underscores
    s3 = re.sub('_+', '_', s2)
    # Convert to lowercase
    return s3.lower()


def add_element_type_suffix(description: str, element_type: str) -> str:
    """Add element type suffix to property name.

    Pattern: {description}_{element_type}
    Avoids redundant suffixes like "email_email".

    Args:
        description: Element description or text
        element_type: Type of element (button, input, link, etc.)

    Returns:
        Name with type suffix in snake_case
    """
    # First convert description to snake_case
    base_name = to_snake_case(remove_special_characters(description))

    # Avoid redundant suffixes (e.g., "email" + "email" → just "email")
    # This happens with input[type="email"] where placeholder is "Email"
    if base_name.endswith(f"_{element_type}"):
        name = base_name
    elif base_name == element_type:
        name = base_name
    else:
        name = f"{base_name}_{element_type}"

    # Truncate if too long (max 60 chars for readability + room for indices)
    return _truncate_name(name, max_length=60)


def generate_name_from_attributes(element: Dict) -> Optional[str]:
    """Generate property name from element attributes.

    Tries in order: placeholder, aria-label, label text, element text, id, type

    Args:
        element: Element dictionary

    Returns:
        Generated property name or None
    """
    # Priority order for name generation

    # 1. Try placeholder
    if "placeholder" in element:
        text = element["placeholder"]
        element_type = element.get("type", "input")
        result = add_element_type_suffix(text, element_type)
        return _fix_numeric_identifier(result)

    # 2. Try aria-label
    if "aria-label" in element:
        text = element["aria-label"]
        element_type = element.get("type", element.get("tag", "element"))
        result = add_element_type_suffix(text, element_type)
        return _fix_numeric_identifier(result)

    # 3. Try aria_label (with underscore from earlier parsing)
    if "aria_label" in element:
        text = element["aria_label"]
        element_type = element.get("type", element.get("tag", "element"))
        result = add_element_type_suffix(text, element_type)
        return _fix_numeric_identifier(result)

    # 4. Try text content (skip whitespace-only)
    if "text" in element:
        text = element["text"].strip() if isinstance(element["text"], str) else element["text"]
        if text:  # Only proceed if not empty after stripping whitespace
            element_type = element.get("type", element.get("tag", "element"))
            result = add_element_type_suffix(text, element_type)
            return _fix_numeric_identifier(result)

    # 5. Try id
    if "id" in element:
        element_id = element["id"]
        element_type = element.get("type", element.get("tag", "element"))
        result = add_element_type_suffix(element_id, element_type)
        return _fix_numeric_identifier(result)

    # 6. Try type
    if "type" in element:
        element_type = element["type"]
        return _fix_numeric_identifier(element_type)

    # 7. Fall back to tag
    if "tag" in element:
        tag = element["tag"]
        return _fix_numeric_identifier(tag)

    return None


def _truncate_name(name: str, max_length: int = 50) -> str:
    """Truncate name if it exceeds max_length, keeping element type suffix.

    Tries to preserve the element type suffix by truncating the description part.
    E.g.: "very_long_description_button" → "very_long_desc_button"

    Args:
        name: The name to truncate
        max_length: Maximum allowed length (default 50 to account for indices/code)

    Returns:
        Truncated name or original if within limit
    """
    if len(name) <= max_length:
        return name

    # Try to find the last underscore (element type suffix)
    parts = name.rsplit("_", 1)
    if len(parts) == 2:
        desc, element_type = parts
        # Calculate how much space we have for description
        # Reserve 5 chars for potential future indices (_99999)
        available = max_length - len(element_type) - 6
        if available > 8:
            # Truncate description and keep element type
            truncated_desc = desc[:available]
            return f"{truncated_desc}_{element_type}"

    # Fallback: just truncate to max_length
    return name[:max_length]


def _fix_numeric_identifier(name: Optional[str]) -> Optional[str]:
    """Fix identifiers that start with a digit by prefixing with underscore.

    Python identifiers cannot start with digits, so "2FA" → "_2_fa"

    Args:
        name: The identifier name to fix

    Returns:
        Fixed identifier or original if already valid
    """
    if not name:
        return name

    if name[0].isdigit():
        return "_" + name

    return name


def remove_special_characters(text: str) -> str:
    """Remove/replace special characters in text.

    Handles: hyphens, ampersand, parentheses, etc. Replaces with spaces.
    Result is ready for to_snake_case() to convert spaces to underscores.

    Args:
        text: Text with special characters

    Returns:
        Text with special characters replaced by spaces
    """
    if not text:
        return text

    # Replace ampersand with 'and' BEFORE removing anything
    text = text.replace("&", "and")

    # Replace hyphens with spaces
    text = text.replace("-", " ")

    # Replace slashes with spaces
    text = text.replace("/", " ")

    # Replace parentheses with spaces (keep content inside)
    text = text.replace("(", " ").replace(")", " ")

    # Replace colons and currency symbols with spaces (keep numbers/text around them)
    text = re.sub(r'[$:€£¥]', ' ', text)

    # Replace dots (periods) with spaces to separate numbers like "99.99" → "99 99"
    text = text.replace(".", " ")

    # Remove remaining special unicode symbols (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)

    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def handle_duplicate_names(names: List[str]) -> Dict[str, str]:
    """Handle duplicate property names by adding indices.

    For duplicates: "name" (1st) → "name_1", "name" (2nd) → "name_2"
    For unique names: "name" → "name"

    Args:
        names: List of property names (may have duplicates)

    Returns:
        Dictionary mapping index to unique name with indices for duplicates
    """
    result = {}
    name_counts = {}
    name_indices = {}

    # Count total occurrences of each name
    for name in names:
        name_counts[name] = name_counts.get(name, 0) + 1

    # Create unique names for each occurrence
    for idx, name in enumerate(names):
        if name_counts[name] > 1:
            # Multiple occurrences - add index suffix
            if name not in name_indices:
                name_indices[name] = 1
            else:
                name_indices[name] += 1

            unique_name = f"{name}_{name_indices[name]}"
            result[idx] = unique_name
        else:
            # Single occurrence - keep as is (no index)
            result[idx] = name

    return result


def is_valid_python_identifier(name: str) -> bool:
    """Check if name is valid Python identifier.

    Rules: starts with letter/underscore, no keywords, alphanumeric + underscore

    Args:
        name: Name to validate

    Returns:
        True if valid Python identifier
    """
    if not name:
        return False

    # Check if it's a Python keyword
    if keyword.iskeyword(name):
        return False

    # Check if it's a valid identifier
    return name.isidentifier()


def format_code_line(code: str, indent: int = 0) -> str:
    """Format code line with proper indentation.

    Args:
        code: Code line
        indent: Indentation level (0=no indent, 1=4 spaces, etc.)

    Returns:
        Formatted code line
    """
    # Add indentation (4 spaces per level)
    indentation = "    " * indent
    return indentation + code


def is_meaningful_container(element: Dict) -> bool:
    """Determine if a container (div, span) is meaningful or generic.

    Generic containers without unique identifiers are filtered out.
    Meaningful containers have component-specific classes or semantic meaning.

    Args:
        element: Element dictionary

    Returns:
        True if container should be included in Page Object
    """
    tag = element.get("tag", "").lower()

    # Only apply filtering to div and span
    if tag not in ("div", "span"):
        return True

    # Has id or data-testid → meaningful
    if element.get("id") or element.get("data-testid"):
        return True

    # Check class names for meaningful components
    classes = element.get("class", [])
    if isinstance(classes, str):
        classes = classes.split()

    if not classes:
        return False

    meaningful_patterns = {
        "dropdown", "modal", "dialog", "alert", "toast",
        "menu", "navigation", "sidebar", "nav",
        "header", "footer", "main",
        "card", "panel", "section", "container",
        "form", "input", "button",
        "list", "item", "row", "col",
        "wrapper", "content", "inner",
        "popup", "overlay", "backdrop",
        "tabs", "tab", "accordion",
        "carousel", "slider", "gallery",
        "breadcrumb", "pagination", "search",
        "filter", "sort", "group",
    }

    for cls in classes:
        cls_lower = cls.lower()
        for pattern in meaningful_patterns:
            if pattern in cls_lower:
                return True

    # Has aria-label or aria-describedby → meaningful
    if element.get("aria-label") or element.get("aria-describedby"):
        return True

    # Has role → meaningful
    if element.get("role"):
        return True

    return False

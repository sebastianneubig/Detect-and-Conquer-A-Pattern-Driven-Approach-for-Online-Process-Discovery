from typing import List, Tuple, Literal, Self
import re

from src.utils.operators import Operators


class PatternNode:
    def __init__(self,
                 node_type: Literal["AND", "OR", "SEQ", "*", "NOT", "event", "condition", "TEMPLATE"],
                 children: List[Self] = None):
        """
        Initialize a PatternNode with a type and optional list of children.

        :param node_type: The type of the node, e.g., "AND", "OR", "SEQ", "*", "NOT", or an event/condition.
        :param children: A list of child PatternNodes.
        """
        self.node_type = node_type
        self.children = children if children else []

    def __repr__(self) -> str:
        """
        Return a string representation of the PatternNode.

        :return: A string representing the node and its children.
        """
        suffix = self.node_type
        prefix = f"{', '.join(map(str, self.children))}"
        if len(self.children) == 0:
            return f"{suffix}"
        return f"{suffix}({prefix})"


def parse_node(pattern: str) -> Tuple[PatternNode, str]:
    """
    Parse a pattern string into a PatternNode and return the remaining pattern string.

    :param pattern: The pattern string to parse.
    :return: A tuple containing the parsed PatternNode and the remaining pattern string.
    :raises ValueError: If the pattern format is unexpected.
    """
    pattern = pattern.strip()

    for operator in Operators.OPERATORS:
        if pattern.startswith(f"{operator}("):
            return parse_logical_node(pattern, operator)

    # Base case: it's an event or condition or template
    match = re.match(r"(\w+)", pattern)
    if match:
        node = PatternNode(match.group(1))
        return node, pattern[match.end():]
    else:
        # Check if it's a template block
        template_match = re.search(r"{{\s*(\w+)\.\w+\s*}}", pattern)
        if template_match:
            # Create a node with the event or condition name
            node = PatternNode("∀" + template_match.group(1))
            remaining_pattern = pattern[template_match.end():]
            return node, remaining_pattern.strip()

        if pattern.startswith("{%") and "%}" in pattern:
            # Skip over the template block
            end_template_index = pattern.find("%}") + 2
            remaining_pattern = pattern[end_template_index:]
            return PatternNode("TEMPLATE", []), remaining_pattern.strip()
        else:
            raise ValueError(f"Unexpected pattern format: {pattern}")


def parse_logical_node(pattern_element: str, node_type: str) -> Tuple[PatternNode, str]:
    """
    Parse a logical node from the pattern string.

    :param pattern_element: The pattern string starting with a logical node.
    :param node_type: The type of logical node, e.g., "AND", "OR", "SEQ", "*", or "NOT".
    :return: A tuple containing the parsed logical PatternNode and the remaining pattern string.
    """
    assert pattern_element.startswith(f"{node_type}(")
    pattern_element = pattern_element[len(node_type) + 1:]  # Skip over "AND(", "OR(", etc.

    children: List[PatternNode] = []
    while not pattern_element.startswith(")"):
        # Detect and handle templates
        if pattern_element.strip().startswith("{%"):
            # Skip over the template block
            end_template_index = pattern_element.find("%}") + 2
            pattern_element = pattern_element[end_template_index:].strip()
            continue

        child, pattern_element = parse_node(pattern_element)
        # Only add non-template children
        if child.node_type != "TEMPLATE":
            children.append(child)
        pattern_element = pattern_element.strip()
        if pattern_element.startswith(","):
            pattern_element = pattern_element[1:].strip()  # Skip over ","

    pattern_element = pattern_element[1:]  # Skip over ")"
    return PatternNode(node_type, children), pattern_element


def parse_pattern(pattern: str) -> PatternNode:
    """
    Parse a full pattern string into a root PatternNode.

    :param pattern: The pattern string to parse.
    :return: The root PatternNode of the parsed pattern.
    :raises ValueError: If there is unexpected remaining content in the pattern string.
    """
    root, remaining_pattern = parse_node(pattern)
    if remaining_pattern.strip():
        raise ValueError(f"Unexpected remaining pattern content: {remaining_pattern}")
    return root



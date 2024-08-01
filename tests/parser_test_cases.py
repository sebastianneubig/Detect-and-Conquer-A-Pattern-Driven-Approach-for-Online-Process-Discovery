from src.parsers.pattern_parser import parse_pattern

TEST_PATTERN_1 = """
AND(
    event1,
    event2
)
"""

TEST_PATTERN_2 = """
OR(
    event1,
    event2
)
"""

TEST_PATTERN_3 = """
AND(
    OR(
        event1,
        event2
    ), 
    AND(
        condition1,
        condition2
    )
)
"""

TEST_PATTERN_4 = """
OR(
    AND(
        event1,
        event2
    ), 
    OR(
        condition1,
        condition2
    )
)
"""

TEST_PATTERN_5 = """
AND(
    OR(
        event1,
        AND(
            event2,
            condition1
        )
    ),
    AND(
        condition2,
        OR(
            event3,
            event4
        )
    )
)
"""

TEST_PATTERN_8 = """
AND(
    event1,
    OR(
        event2,
        condition1
    ),
    AND(
        condition2,
        event3
    )
)
"""

TEST_PATTERN_9 = """
OR(
    event1,
    event2,
    condition1,
    condition2,
    event3
)
"""

TEST_PATTERN_10 = """
AND(
    AND(
        condition1,
        condition2
    ),
    AND(
        condition3,
        condition4
    )
)
"""

TEST_PATTERN_11: str = """
AND(
    OR(
      {% for event in events %} {{ event.name }} {% endfor %}
    ), 
    AND(
      {% for condition in conditions %} {{ condition.name }} {% endfor %}
    )
)
"""

TEST_PATTERN_12 = """
AND(
    OR(
        event1,
        AND(
            event2,
            event1
        )
    ),
    AND(
        {% for event in event %} {{ event.name }} {% endfor %}
    )
) 
"""

if __name__ == "__main__":
    for i, pattern in enumerate([
        TEST_PATTERN_1, TEST_PATTERN_2, TEST_PATTERN_3, TEST_PATTERN_4,
        TEST_PATTERN_5, TEST_PATTERN_8,
        TEST_PATTERN_9, TEST_PATTERN_10, TEST_PATTERN_11, TEST_PATTERN_12
    ]):
        try:
            pattern_tree = parse_pattern(pattern)
            print(f"Test Case {i + 1}: Success")
            print(pattern_tree)
        except ValueError as e:
            print(f"Test Case {i + 1}: Error - {e}")

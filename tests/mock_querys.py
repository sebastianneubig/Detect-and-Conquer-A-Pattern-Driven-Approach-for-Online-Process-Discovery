
TEST_STRUCTURAL_CEP: str = """
AND(
    OR(
      {% for event in events %} {{ event.name }} {% endfor %}
    ), 
    AND(
      {% for condition in conditions %} {{ condition.name }} {% endfor %}
    )
)
""".replace("\n", "")

TEST_TEMPLATE_CEP: str = """
PATTERN AND(
    OR(
      {% for event in events %} {{ event.name }} {% endfor %}
    ), 
    AND(
      {% for condition in conditions %}{{ condition.name }} {% endfor %}
    )
)

WHERE (
      {% for event in events %}
        {% for condition in conditions %}
          related({{ event.var }}, {{ condition.var }}) OR
        {% endfor %}
       AND
      {% endfor %}
)

WITHIN {{ time }} minutes
""".replace("\n", "")
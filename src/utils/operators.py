class AndOperator:
    def __str__(self):
        return "AND"


class OrOperator:
    def __str__(self):
        return "OR"


class SeqOperator:
    def __str__(self):
        return "SEQ"


class KleeneClosureOperator:
    def __str__(self):
        return "*"


class NegationOperator:
    def __str__(self):
        return "NOT"


class Operators(object):
    AND = "AND"
    OR = "OR"
    SEQ = "SEQ"
    KLEENE_CLOSURE = "*"
    NEGATION = "NOT"
    OPERATORS = [AND, OR, SEQ, KLEENE_CLOSURE, NEGATION]

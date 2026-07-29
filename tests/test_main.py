import math
from main import SudokuMathApp


class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, text=None, **kwargs):
        if text is not None:
            self.text = text


class DummyEntry:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def delete(self, a, b=None):
        pass

    def insert(self, i, v):
        self._value = v

    def focus_set(self):
        pass

    def bind(self, *a, **kw):
        pass


class DummyFeedback(DummyLabel):
    def configure(self, text=None, fg=None):
        super().configure(text=text)


class DummyRoot:
    def after(self, ms, func):
        # no-op to avoid scheduling/calling GUI callbacks during tests
        return None


def test_make_solution_is_valid():
    grid = SudokuMathApp._make_solution()
    assert len(grid) == 9
    # each row contains numbers 1..9
    for row in grid:
        assert set(row) == set(range(1, 10))
    # each column contains numbers 1..9
    for c in range(9):
        assert set(grid[r][c] for r in range(9)) == set(range(1, 10))


def test_operator_for_level_bands():
    inst = object.__new__(SudokuMathApp)
    # Test the six intro operators by band (math_var // 10)
    expected = ["+", "-", "*", "/", "**", "sqrt"]
    for band, op in enumerate(expected):
        inst.math_var = band * 10
        assert inst._operator_for_level() == op
    # after intro, returns 'multi'
    inst.math_var = 60
    assert inst._operator_for_level() == "multi"


def test_multi_operators_returns_tuple_and_grows():
    inst = object.__new__(SudokuMathApp)
    # select a math_var that is after intro so we exercise _multi_operators
    inst.math_var = 70
    ops = inst._multi_operators()
    assert isinstance(ops, tuple)
    assert len(ops) >= 2


def test_new_question_and_submit_correct_answer_increments_math_var():
    inst = object.__new__(SudokuMathApp)
    inst.math_var = 0
    inst.math_digit_size = 1
    inst.current_answer = 0.0
    inst.question_label = DummyLabel()
    inst.answer_entry = DummyEntry()
    inst.feedback = DummyFeedback()
    inst.root = DummyRoot()
    # avoid any GUI side effects
    inst.reveal_random_cell = lambda: None
    inst.hints_used = 0
    inst.failure_streak = 0

    inst.new_question()
    # answer with the floored current_answer (one accepted value)
    inst.answer_entry._value = str(math.floor(inst.current_answer))
    prev_math_var = inst.math_var
    prev_math_digit = inst.math_digit_size

    inst.submit_answer()

    assert inst.math_var == prev_math_var + 1
    assert inst.math_digit_size == prev_math_digit + 1
    assert inst.feedback.text is not None and "Correct" in inst.feedback.text


def test_submit_wrong_answer_decreases_on_streak():
    inst = object.__new__(SudokuMathApp)
    inst.math_var = 5
    inst.math_digit_size = 2
    inst.current_answer = 10.0
    inst.question_label = DummyLabel()
    inst.answer_entry = DummyEntry("999")
    inst.feedback = DummyFeedback()
    inst.root = DummyRoot()
    inst.reveal_random_cell = lambda: None
    inst.failure_streak = 0

    # first wrong attempt: failure_streak increments
    inst.submit_answer()
    assert inst.failure_streak == 1
    # second wrong attempt: triggers adjustment and resets failure_streak
    inst.answer_entry._value = "999"
    inst.submit_answer()
    assert inst.failure_streak == 0
    # math_var should not have increased (it may decrease)
    assert inst.math_var <= 5

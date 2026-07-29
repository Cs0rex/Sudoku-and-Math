"""Sudoku and Math - an adaptive Sudoku game with math-powered hints."""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import messagebox


BACKGROUND = "#ffe8d1"
PANEL = "#fff3e8"
BLACK = "#111111"
WRONG = "#c62828"
GIVEN = "#444444"


class SudokuMathApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku and Math")
        self.root.configure(bg=BACKGROUND)
        self.root.geometry("1100x720")
        self.root.minsize(930, 620)

        # Adaptive values. s_var is deliberately a float; only its floored
        # value is used while deciding the number of visible Sudoku cells.
        self.s_var = 0.0
        self.math_var = 0
        self.math_digit_size = 1
        self.failure_streak = 0
        self.hints_used = 0
        self.solution: list[list[int]] = []
        self.puzzle: list[list[int]] = []
        self.entries: list[list[tk.Entry]] = []
        self.current_answer: float = 0

        self._build_layout()
        self.new_game()

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, bg=BACKGROUND)
        container.pack(fill="both", expand=True, padx=18, pady=18)
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1, minsize=300)
        container.grid_rowconfigure(0, weight=1)

        sudoku_area = tk.Frame(container, bg=BACKGROUND)
        sudoku_area.grid(row=0, column=0, sticky="nsew")
        # A fixed-size board keeps every tile square, independent of window size.
        self.sudoku_frame = tk.Frame(sudoku_area, bg=BLACK, width=540, height=540)
        self.sudoku_frame.grid(row=0, column=0, pady=12)
        self.sudoku_frame.grid_propagate(False)
        sudoku_area.grid_columnconfigure(0, weight=1)

        self.hint_frame = tk.Frame(container, bg=PANEL, highlightbackground=BLACK,
                                   highlightthickness=1)
        self.hint_frame.grid(row=0, column=1, sticky="nsew", padx=(18, 0))
        self.hint_frame.grid_columnconfigure(0, weight=1)
        self.hint_frame.grid_rowconfigure(2, weight=1)

        tk.Label(self.hint_frame, text="Hint", bg=PANEL, fg=BLACK,
                 font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="ne", padx=18, pady=16)

        middle = tk.Frame(self.hint_frame, bg=PANEL)
        middle.grid(row=2, column=0, sticky="nsew", padx=18)
        middle.grid_columnconfigure(0, weight=1)

        question_row = tk.Frame(middle, bg=PANEL)
        question_row.pack(fill="x")
        self.question_label = tk.Label(question_row, bg=PANEL, fg=BLACK,
                                       font=("Arial", 17), wraplength=250, justify="center")
        self.question_label.pack(side="left", fill="x", expand=True)
        tk.Button(question_row, text="Reroll", command=self.new_question, bg=BACKGROUND,
                  fg=BLACK, relief="flat", highlightbackground=BLACK, highlightthickness=1,
                  padx=8, pady=5).pack(side="right", padx=(8, 0))

        self.answer_entry = tk.Entry(middle, justify="center", font=("Arial", 18),
                                     relief="flat", highlightbackground=BLACK, highlightthickness=1)
        self.answer_entry.pack(fill="x", pady=(24, 8), ipady=7)
        self.answer_entry.bind("<Return>", self.submit_answer)
        tk.Button(middle, text="Submit", command=self.submit_answer, bg=BACKGROUND, fg=BLACK,
                  relief="flat", highlightbackground=BLACK, highlightthickness=1,
                  pady=7).pack(fill="x")

        self.feedback = tk.Label(middle, text="", bg=PANEL, fg=BLACK, font=("Arial", 10), wraplength=250)
        self.feedback.pack(pady=(12, 0))

    # ----- Sudoku -----------------------------------------------------
    def new_game(self) -> None:
        self.hints_used = 0
        self.solution = self._make_solution()
        visible = max(9, 42 - math.floor(self.s_var))
        locations = random.sample(range(81), visible)
        self.puzzle = [[0] * 9 for _ in range(9)]
        for location in locations:
            row, col = divmod(location, 9)
            self.puzzle[row][col] = self.solution[row][col]
        self._draw_board()
        self.new_question()

    @staticmethod
    def _make_solution() -> list[list[int]]:
        """Generate a randomized valid completed Sudoku grid."""
        base = 3
        pattern = lambda r, c: (base * (r % base) + r // base + c) % 9
        rows = [g * base + r for g in random.sample(range(base), base)
                for r in random.sample(range(base), base)]
        cols = [g * base + c for g in random.sample(range(base), base)
                for c in random.sample(range(base), base)]
        nums = random.sample(range(1, 10), 9)
        return [[nums[pattern(r, c)] for c in cols] for r in rows]

    def _draw_board(self) -> None:
        for widget in self.sudoku_frame.winfo_children():
            widget.destroy()
        self.entries = []
        # Three block frames form the deliberately heavier 3 × 3 grid borders.
        for block_row in range(3):
            self.sudoku_frame.grid_rowconfigure(block_row, weight=1, uniform="block")
            for block_col in range(3):
                self.sudoku_frame.grid_columnconfigure(block_col, weight=1, uniform="block")
                block = tk.Frame(self.sudoku_frame, bg=BLACK, highlightbackground=BLACK,
                                 highlightthickness=3)
                block.grid(row=block_row, column=block_col, sticky="nsew")
                for inner_row in range(3):
                    block.grid_rowconfigure(inner_row, weight=1, uniform="cell")
                    for inner_col in range(3):
                        block.grid_columnconfigure(inner_col, weight=1, uniform="cell")
                        row, col = block_row * 3 + inner_row, block_col * 3 + inner_col
                        given = self.puzzle[row][col]
                        cell = tk.Frame(block, bg=BLACK, highlightbackground=BLACK, highlightthickness=1)
                        cell.grid(row=inner_row, column=inner_col, sticky="nsew")
                        entry = tk.Entry(cell, justify="center", width=2, font=("Arial", 18, "bold"),
                                         bg=PANEL if given else "white", fg=GIVEN if given else BLACK,
                                         relief="flat", highlightthickness=0)
                        entry.pack(fill="both", expand=True, padx=1, pady=1)
                        if given:
                            entry.insert(0, str(given))
                            entry.configure(state="readonly")
                        else:
                            entry.bind("<KeyRelease>", lambda event, r=row, c=col: self.check_cell(r, c))
                            entry.bind("<FocusOut>", lambda event, r=row, c=col: self.check_cell(r, c))
                        if len(self.entries) <= row:
                            self.entries.append([])
                        self.entries[row].append(entry)

    def check_cell(self, row: int, col: int) -> None:
        entry = self.entries[row][col]
        value = entry.get().strip()
        if not value:
            entry.configure(fg=BLACK)
            return
        if value.isdigit() and len(value) == 1 and int(value) == self.solution[row][col]:
            entry.configure(fg=BLACK)
            self._check_completion()
        else:
            entry.configure(fg=WRONG)

    def _check_completion(self) -> None:
        for row in range(9):
            for col in range(9):
                if self.entries[row][col].get().strip() != str(self.solution[row][col]):
                    return
        increase = max(0.0, 1.0 - 0.1 * self.hints_used)
        self.s_var += increase
        messagebox.showinfo("Sudoku complete", f"Puzzle solved. Sudoku difficulty increased by {increase:.1f}.")
        self.new_game()

    def reveal_random_cell(self) -> None:
        empty = [(r, c) for r in range(9) for c in range(9) if self.puzzle[r][c] == 0]
        if not empty:
            return
        row, col = random.choice(empty)
        self.puzzle[row][col] = self.solution[row][col]
        self.hints_used += 1
        entry = self.entries[row][col]
        entry.delete(0, tk.END)
        entry.insert(0, str(self.solution[row][col]))
        entry.configure(state="readonly", fg=GIVEN, bg=PANEL)

    # ----- Math hints -------------------------------------------------
    def _operator_for_level(self) -> str:
        # Every ten successful difficulty levels moves to the next operator.
        # After the six introductory operators, two-operation expressions begin.
        intro = ["+", "-", "*", "/", "**", "sqrt"]
        band = self.math_var // 10
        return intro[band] if band < len(intro) else "multi"

    def _multi_operators(self) -> tuple[str, ...]:
        """Return the operator pattern used after the introductory six bands."""
        band_after_intro = self.math_var // 10 - 6
        # This begins with the requested order. Further patterns follow it in
        # a stable order, then gain another operator every 25 threshold bands.
        seed = [("+", "+"), ("-", "+"), ("+", "-"), ("*", "+"),
                ("-", "*"), ("*", "*"), ("+", "/")]
        all_two = [(a, b) for a in ("+", "-", "*", "/", "**")
                   for b in ("+", "-", "*", "/", "**")]
        patterns = seed + [pair for pair in all_two if pair not in seed]
        operator_count = 2 + max(0, band_after_intro // len(patterns))
        base = patterns[band_after_intro % len(patterns)]
        return tuple((base * ((operator_count + 1) // 2))[:operator_count])

    def new_question(self) -> None:
        operator = self._operator_for_level()
        # Keep numbers practical for a visual, human-solvable game. The size
        # state still follows the adaptive rules and is bounded at six digits.
        digits = min(6, max(1, self.math_digit_size))
        low = 10 ** (digits - 1) if digits > 1 else 1
        high = 10 ** digits - 1
        if operator == "+":
            a, b = random.randint(low, high), random.randint(low, high)
            text, answer = f"{a} + {b} = ?", a + b
        elif operator == "-":
            a, b = sorted((random.randint(low, high), random.randint(low, high)), reverse=True)
            text, answer = f"{a} − {b} = ?", a - b
        elif operator == "*":
            a, b = random.randint(low, high), random.randint(1, min(high, 99))
            text, answer = f"{a} × {b} = ?", a * b
        elif operator == "/":
            divisor = random.randint(2, min(high, 99))
            quotient = random.randint(low, high)
            dividend = divisor * quotient + random.randint(1, divisor - 1)
            text, answer = f"{dividend} ÷ {divisor} = ?", dividend / divisor
        elif operator == "**":
            a, b = random.randint(2, 9), random.randint(2, 3)
            text, answer = f"{a} ** {b} = ?", a ** b
        elif operator == "sqrt":
            # A non-perfect-square root makes the stated floor/ceiling rule useful.
            number = random.randint(low, high)
            text, answer = f"√{number} = ?", math.sqrt(number)
        else:
            operators = self._multi_operators()
            # Each added operator also adds an operand. Evaluate from left to
            # right so every displayed multi-operator question is unambiguous.
            values = [random.randint(low, high) for _ in range(len(operators) + 1)]
            result = float(values[0])
            pieces = [str(values[0])]
            for symbol, value in zip(operators, values[1:]):
                if symbol == "+":
                    result += value
                    shown = "+"
                elif symbol == "-":
                    result -= value
                    shown = "−"
                elif symbol == "*":
                    result *= value
                    shown = "×"
                elif symbol == "/":
                    # Avoid a zero divisor and retain the floor/ceiling rule.
                    result /= max(1, value)
                    shown = "÷"
                else:
                    # Keep exponent questions tractable even at high levels.
                    value = random.randint(2, 3)
                    result = min(abs(result), 9) ** value
                    shown = "**"
                pieces.extend((shown, str(value)))
            text, answer = " ".join(pieces) + " = ?", result
        self.current_answer = answer
        self.question_label.configure(text=text)
        self.answer_entry.delete(0, tk.END)
        self.feedback.configure(text="")
        self.answer_entry.focus_set()

    def submit_answer(self, _event: object | None = None) -> None:
        try:
            user_answer = int(self.answer_entry.get().strip())
        except ValueError:
            self.feedback.configure(text="Enter a whole-number answer.", fg=WRONG)
            return
        accepted = {math.floor(self.current_answer), math.ceil(self.current_answer)}
        if user_answer in accepted:
            old_band = self.math_var // 10
            self.math_var += 1
            self.math_digit_size += 1
            new_band = self.math_var // 10
            # Entering square-root level keeps digit size; every other threshold
            # transition reduces it to 20% (rounded down, minimum one digit).
            entering_sqrt = self._operator_for_level() == "sqrt"
            if new_band > old_band and not entering_sqrt:
                self.math_digit_size = max(1, math.floor(self.math_digit_size * 0.2))
            self.failure_streak = 0
            self.reveal_random_cell()
            self.feedback.configure(text="Correct — one cell was revealed.", fg=BLACK)
            self.root.after(700, self.new_question)
        else:
            self.failure_streak += 1
            if self.failure_streak >= 2:
                self.math_var = max(0, self.math_var - 1)
                self.math_digit_size = max(1, self.math_digit_size - 1)
                self.failure_streak = 0
                self.feedback.configure(text="Incorrect. Math difficulty decreased by 1.", fg=WRONG)
            else:
                self.feedback.configure(text="Incorrect. Try the next question.", fg=WRONG)
            self.root.after(900, self.new_question)


if __name__ == "__main__":
    window = tk.Tk()
    SudokuMathApp(window)
    window.mainloop()

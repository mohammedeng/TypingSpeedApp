"""Graphical interface for the typing-speed test application.

The :class:`Screen` window presents practice text, tracks typing progress,
manages the countdown, and displays the final speed and accuracy.
"""

import math
import time
from tkinter import Event

import customtkinter as ctk

from typing_test import TypingTest

# Default and minimum test duration, in minutes.
DEFAULT_MINUTES = 1
MIN_MINUTES = 1
ENTRY_PLACEHOLDER = "Typing The Word Here..."
WARNING_SECONDS = 10
WARNING_COLOR = "red"

# Configure the overall appearance of the application.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Screen(ctk.CTk):
    """Main window of the typing speed test application.

    The screen presents a sample paragraph, a text entry area, and timing
    controls. It highlights the active word and updates the user's score while
    they type.
    """

    def __init__(self):
        """Initialize the app window and all related widgets and state."""
        super().__init__()

        # The model owns the paragraph, word progression, and score data.
        self.typing_test = TypingTest()
        self.finished = False

        # Configure the fixed-size application window.
        self.title("Typing Speed Test")
        self.geometry("800x600")
        self.resizable(False, False)

        # Timer state for the current test.
        self.entry_word = ""
        self.timer = None
        self.test_minutes = DEFAULT_MINUTES
        self.start_time = None

        # Build the interface and highlight the first target word.
        self.create_widgets()
        self.highlight_current_word()
        # Set focus after the window is created so typing can begin immediately.
        self.after(1000, self.entry.focus_set)

    def calculate_speed(self) -> None:
        """Finish the test, stop the timer, and show speed and accuracy.

        Speed is measured in words per minute using the real elapsed time, since
        the test can end before the timer does (when all words are typed).
        Accuracy is the percentage of correct words among all submitted words.
        """
        self.finished = True
        elapsed_minutes = (time.monotonic() - self.start_time) / 60
        wpm = self.typing_test.wpm(elapsed_minutes)
        accuracy = self.typing_test.accuracy()

        self.entry.delete(0, "end")
        self.entry.insert(0, f"Speed: {wpm:.0f} wpm | accuracy: {accuracy:.0f}%")
        self.entry.configure(state="disabled")
        self.cancel_timer()

    def highlight_current_word(self) -> None:
        """Highlight the active word in the paragraph and scroll to it."""
        start_pos = self.typing_test.word_starts[self.typing_test.word_index]
        word = self.typing_test.current_word
        end_pos = start_pos + len(word)

        self.show_text.tag_remove("background", "1.0", "end")
        self.show_text.tag_add("background", f"1.{start_pos}", f"1.{end_pos}")
        self.show_text.see(f"1.{start_pos}")

    def highlight_missing_letters(self, word_index: int, typed_word: str) -> None:
        """Mark omitted letters in a submitted word as incorrect.

        This marks only the target's trailing letters that were not typed.

        Args:
            word_index: Index of the submitted target word.
            typed_word: Text entered by the user for that word.
        """
        word = self.typing_test.list_words[word_index]
        start = self.typing_test.word_starts[word_index]

        for i in range(len(typed_word), len(word)):
            char_pos = start + i
            self.show_text.tag_add("wrong", f"1.{char_pos}", f"1.{char_pos + 1}")

    def highlight_letters(self, word_index: int, typed_word: str) -> None:
        """Color typed characters according to whether they match the target.

        Args:
            word_index: Index of the target word in the paragraph.
            typed_word: Text entered by the user for that word.
        """
        target = self.typing_test.list_words[word_index]
        start = self.typing_test.word_starts[word_index]

        # Clear old coloring for this word before applying the new one.
        self.show_text.tag_remove("correct", f"1.{start}", f"1.{start + len(target)}")
        self.show_text.tag_remove("wrong", f"1.{start}", f"1.{start + len(target)}")

        # Only color letters inside the word; extra letters would spill over.
        for i, ch in enumerate(typed_word[:len(target)]):
            char_pos = start + i
            tag = "correct" if ch == target[i] else "wrong"
            self.show_text.tag_add(tag, f"1.{char_pos}", f"1.{char_pos + 1}")

    def key_press(self, event: Event) -> None:
        """Handle key events during typing.

        The method checks the current input word, starts the timer on first
        character entry, advances to the next word on space, updates highlight
        colors, and ends the challenge when all words are processed.
        """
        if self.finished or self.typing_test.is_finished:
            return

        raw_text = self.entry.get()
        self.entry_word = raw_text.strip()
        if event.char.isalnum() and self.timer is None:
            self.start_timer()

        result = self.typing_test.check_word(raw_text)
        if result is not None:
            typed_word, is_correct, remainder = result

            # Keep characters typed after the space as the start of the next word.
            self.entry.delete(0, "end")
            self.entry.insert(0, remainder)

            # A space with no word before it: ignore it.
            if is_correct is None:
                return
            finished_index = self.typing_test.word_index - 1

            # Color the completed word, including its final character.
            self.highlight_letters(finished_index, typed_word)

            if not is_correct:
                self.highlight_missing_letters(finished_index, typed_word)

            if self.typing_test.is_finished:
                self.calculate_speed()
                return

            # Keep characters typed after the separating space as the next input.
            self.entry_word = remainder

        # Highlight the active word and color the letters typed so far.
        self.highlight_current_word()
        self.highlight_letters(self.typing_test.word_index, self.entry_word)

    def create_widgets(self) -> None:
        """Create and arrange all visual components of the typing screen."""
        self.lbl = ctk.CTkLabel(
            master=self,
            text="Typing Speed Test",
            font=("arial", 40, "bold"),
            width=700,
            height=50,
        )
        self.lbl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

        self.min_lbl = ctk.CTkLabel(
            master=self,
            text="Min",
            font=("arial", 20, "bold"),
            width=30,
            height=10,
        )
        self.min_lbl.grid(row=1, column=0, sticky="nsew", padx=(90, 0), pady=10)

        # Duration selector for the timing window of the typing test.
        self.min_entry = ctk.CTkEntry(master=self, placeholder_text="minute", width=100, height=10)
        self.min_entry.insert(0, str(DEFAULT_MINUTES))
        self.min_entry.grid(row=1, column=0, padx=(250, 0), pady=(5, 0))
        self.min_entry.bind("<KeyRelease>", self.on_minutes_change)

        # Label that shows the remaining time during the test.
        self.timer_lbl = ctk.CTkLabel(
            master=self,
            text=self.format_time(DEFAULT_MINUTES * 60),
            font=("arial", 28, "bold"),
        )
        self.timer_lbl.grid(row=1, column=1, padx=(0, 150), pady=10)
        # Remember the normal color so it can be restored after a red warning.
        self.timer_default_color = self.timer_lbl.cget("text_color")

        # Display the generated paragraph to be typed.
        self.show_text = ctk.CTkTextbox(
            master=self,
            font=("arial", 30, "bold"),
            width=700,
            height=200,
            wrap="word",
        )
        self.show_text.insert("1.0", self.typing_test.text_words)
        self.show_text.configure(state="disabled")
        self.show_text.grid(row=2, column=0, sticky="nsew", padx=(50, 0), pady=10, columnspan=2)

        # Text styling for highlighting correct, incorrect, and current words.
        self.show_text.tag_config("background", background="green")
        self.show_text.tag_config("correct", foreground="orange")
        self.show_text.tag_config("wrong", foreground="red")

        # Input field where the user types the sentence/words.
        self.entry = ctk.CTkEntry(
            master=self,
            width=700,
            justify="center",
            placeholder_text=ENTRY_PLACEHOLDER,
            height=100,
            font=("arial", 40, "bold"),
        )
        self.entry.bind("<KeyRelease>", self.key_press)
        self.entry.grid(row=4, column=0, sticky="nsew", padx=(50, 0), pady=10, columnspan=2)

        # Reset button to generate a new paragraph and clear state.
        self.btn = ctk.CTkButton(
            master=self,
            text="Reset",
            font=("arial", 20, "bold"),
            width=100,
            height=30,
            command=self.reset,
        )
        self.btn.grid(row=5, column=1, padx=(0, 300), pady=10)

    def cancel_timer(self) -> None:
        """Stop the active timer if it exists."""
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def format_time(self, seconds: float) -> str:
        """Return a number of seconds formatted as MM:SS."""
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"

    def show_remaining(self, seconds: float) -> None:
        """Show the remaining time, in red when it is nearly over."""
        color = WARNING_COLOR if seconds <= WARNING_SECONDS else self.timer_default_color
        self.timer_lbl.configure(text=self.format_time(seconds), text_color=color)

    def on_minutes_change(self, event: Event) -> None:
        """Refresh the countdown label when the minutes field is edited.

        Only applies before the test starts, and ignores empty or invalid text
        so the user can keep typing without the field being rewritten.
        """
        if self.timer is not None or self.finished:
            return

        text = self.min_entry.get().strip()
        if text.isdigit():
            self.show_remaining(max(MIN_MINUTES, int(text)) * 60)

    def read_minutes(self) -> int:
        """Read the duration from the minutes entry, falling back to the default."""
        try:
            return max(MIN_MINUTES, int(self.min_entry.get()))
        except ValueError:
            self.min_entry.delete(0, "end")
            self.min_entry.insert(0, str(DEFAULT_MINUTES))
            return DEFAULT_MINUTES

    def tick(self) -> None:
        """Update the countdown label and end the test when time runs out."""
        elapsed = time.monotonic() - self.start_time
        remaining = self.test_minutes * 60 - elapsed

        if remaining <= 0:
            self.show_remaining(0)
            self.calculate_speed()
            return

        # Round up so the label shows 00:01 until the very end.
        self.show_remaining(math.ceil(remaining))
        self.timer = self.after(200, self.tick)

    def start_timer(self) -> None:
        """Start the countdown and record the start time."""
        self.test_minutes = self.read_minutes()
        self.start_time = time.monotonic()
        self.tick()

    def reset(self) -> None:
        """Reset the challenge and generate a fresh paragraph."""
        self.finished = False
        self.typing_test.reset()
        self.show_text.configure(state="normal")
        self.show_text.delete("1.0", "end")
        self.show_text.insert("1.0", self.typing_test.text_words)
        for tag in ("correct", "wrong", "background"):
            self.show_text.tag_remove(tag, "1.0", "end")
        self.show_text.configure(state="disabled")
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.configure(placeholder_text=ENTRY_PLACEHOLDER)

        self.show_remaining(self.read_minutes() * 60)
        self.cancel_timer()
        self.highlight_current_word()
        # Return keyboard focus to the entry so the user can type immediately.
        self.entry.focus()

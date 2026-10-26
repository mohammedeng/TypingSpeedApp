"""Typing speed test GUI application.

This module builds the main window for a typing challenge using
``customtkinter``. It generates a random paragraph, tracks the current word,
visualizes typing progress, and reports the user's typing speed (WPM) and
accuracy when the test ends.
"""

import customtkinter as ctk
import time
from create_text import Paragraph

# Configuration values used across the app.
SENTENCES_PER_TEXT = 10   # Length of the generated paragraph.
DEFAULT_MINUTES = 1       # Default test duration.
ENTRY_PLACEHOLDER = "Typing The Word Here..."

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

        # Track typed words grouped by correctness.
        self.correct_word_list = []
        self.wrong_word_list = []

        # Generate challenge text and split it into words for comparison.
        self.paragraph = Paragraph()
        self.load_new_text()

        # Window configuration.
        self.title("Typing Speed Test")
        self.geometry("800x600")
        self.resizable(False, False)
        self.word_index = 0
        # Runtime state for the current test.
        self.entry_word = None
        self.current_word = None
        self.timer = None
        self.test_minutes = DEFAULT_MINUTES  # Duration chosen for the current test.
        self.start_time = None  # Set when the first character is typed.

        # Widget setup and runtime state.
        self.styling_screen()
        self.highlight_current_word()
        # Give keyboard focus to the entry once the window is visible,
        # so the user can start typing immediately.
        self.after(1000, self.entry.focus_set)

    def build_word_positions(self):
        """Compute the start index of every word in the paragraph once.

        Stores the result in ``self.word_starts``, where ``word_starts[i]`` is the
        character offset of word ``i`` inside the Textbox. Must be called whenever
        ``self.list_graph`` changes.
    """
        self.word_starts = []
        position = 0
        for word in self.list_graph:
            self.word_starts.append(position)
            position += len(word) + 1  # +1 for the space that follows the word

    def load_new_text(self):
        """Generate a fresh paragraph and rebuild the word data from it."""
        self.text_graph = self.paragraph.create_paragraph(SENTENCES_PER_TEXT)
        self.list_graph = self.text_graph.split(" ")
        self.build_word_positions()

    def highlight_current_word(self):
        """Highlight the active word, scroll it into view, and return its range."""
        # Position of the current word inside the paragraph text.
        start_pos = self.word_starts[self.word_index]
        end_pos = start_pos + len(self.list_graph[self.word_index])

        self.show_text.tag_remove("background", "1.0", "end")
        self.show_text.tag_add("background", f"1.{start_pos}", f"1.{end_pos}")
        self.show_text.see(f"1.{start_pos}")
        return start_pos, end_pos

    def calculate_speed(self):
        """Finish the test, stop the timer, and show speed and accuracy.

        Speed is measured in words per minute using the real elapsed time, since
        the test can end before the timer does (when all words are typed).
        Accuracy is the percentage of correct words among all submitted words.

        Returns:
            None: Displays the result in the entry field, locks it, and cancels
            the timer.
        """

        elapsed_minutes = (time.monotonic() - self.start_time) / 60
        elapsed_minutes = max(elapsed_minutes, 1 / 60)  # avoid dividing by zero
        wpm = len(self.correct_word_list) / elapsed_minutes

        # Accuracy is the share of correct words among all submitted words.
        total_words = len(self.correct_word_list) + len(self.wrong_word_list)
        if total_words > 0:
            accuracy = len(self.correct_word_list) / total_words * 100
        else:
            accuracy = 0

        self.entry.delete(0, "end")
        self.entry.insert(0, f"Speed: {wpm:.0f} wpm | accuracy: {accuracy:.0f}%")
        self.entry.configure(state="disabled")
        self.cancel_timer()

    def key_press(self, event):
        """Handle key events during typing.

        The method checks the current input word, starts the timer on first
        character entry, advances to the next word on space, updates highlight
        colors, and ends the challenge when all words are processed.
        """
        if self.word_index >= len(self.list_graph):
            return

        # Get the raw input from the text box and trim spaces for comparison.
        raw_text = self.entry.get()
        self.entry_word = raw_text.strip()
        self.current_word = self.list_graph[self.word_index]

        # Start a countdown only after the first alphanumeric character is typed.
        if event.char.isalnum() and self.timer is None:
            self.start_timer()

        # When the user presses the space key, the current word is evaluated.
        # Detect a space anywhere in the text (not only at the end), so fast typists
        # who press the next letter before releasing the space key are handled.
        if " " in raw_text:
            # Split at the first space: the part before it is the finished word,
            # and anything after it belongs to the next word.
            typed_word, _, remainder = raw_text.partition(" ")
            remainder = remainder.lstrip()

            # Keep any characters typed after the space inside the entry field,
            # so they become the beginning of the next word instead of being lost.
            self.entry.delete(0, "end")
            self.entry.insert(0, remainder)

            # A space with no word before it: ignore it and wait for real input.
            if not typed_word:
                return

            # Compare the finished word with the expected word and record the result.
            if typed_word == self.current_word:
                self.correct_word_list.append(self.current_word)
            else:
                self.wrong_word_list.append(typed_word)

            # Move on to the next word in the paragraph.
            self.word_index += 1

            # All words are done: end the test and show the speed.
            if self.word_index >= len(self.list_graph):
                self.calculate_speed()
                return

            # Update the state for the new word, including any early characters
            # that were already typed for it.
            self.current_word = self.list_graph[self.word_index]
            self.entry_word = remainder

        # Calculate the text position of the current word in the paragraph.
        start_pos, end_pos = self.highlight_current_word()

        # Apply per-character highlighting to show correct and incorrect letters.
        self.show_text.tag_remove("correct", f"1.{start_pos}", f"1.{end_pos}")
        self.show_text.tag_remove("wrong", f"1.{start_pos}", f"1.{end_pos}")

        # Only color characters that fall inside the current word. Extra characters
        # have no matching position and would spill onto the following words.
        for i, ch in enumerate(self.entry_word[:len(self.current_word)]):
            char_pos = start_pos + i
            if ch == self.current_word[i]:
                self.show_text.tag_add("correct", f"1.{char_pos}", f"1.{char_pos + 1}")
            else:
                self.show_text.tag_add("wrong", f"1.{char_pos}", f"1.{char_pos + 1}")

    def styling_screen(self):
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

        # Display the generated paragraph to be typed.
        self.show_text = ctk.CTkTextbox(
            master=self,
            font=("arial", 30, "bold"),
            width=700,
            height=200,
            wrap="word",
        )
        self.show_text.insert("1.0", self.text_graph)
        self.show_text.configure(state="disabled")
        self.show_text.grid(row=2, column=0, sticky="nsew", padx=(50, 0), pady=10, columnspan=2)

        # Text styling for highlighting correct, incorrect, and current words.
        self.show_text.tag_config("background", background="green")
        self.show_text.tag_config("correct", foreground="white")
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

    def cancel_timer(self):
        """Stop the active timer if it exists."""
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def start_timer(self):

        """Start the countdown and record the start time.
        The duration comes from the minutes' entry. Invalid input falls back to
        one minute. The start time is used later to compute the real WPM.
    """

        try:
            self.test_minutes = max(1, int(self.min_entry.get()))
        except ValueError:
            self.test_minutes = DEFAULT_MINUTES
            self.min_entry.delete(0, "end")
            self.min_entry.insert(0, str(DEFAULT_MINUTES))
        # Remember when the test started so the real elapsed time can be measured.
        self.start_time = time.monotonic()
        self.timer = self.after(self.test_minutes * 60 * 1000, self.calculate_speed)

    def reset(self):
        """Reset the challenge and generate a fresh paragraph."""
        self.load_new_text()
        self.show_text.configure(state="normal")
        self.show_text.delete("1.0", "end")
        self.show_text.insert("1.0", self.text_graph)
        for tag in ("correct", "wrong", "background"):
            self.show_text.tag_remove(tag, "1.0", "end")
        self.show_text.configure(state="disabled")
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.configure(placeholder_text=ENTRY_PLACEHOLDER)


        self.correct_word_list = []
        self.wrong_word_list = []
        self.cancel_timer()
        self.word_index = 0
        self.highlight_current_word()
        # Return keyboard focus to the entry so the user can type immediately.
        self.entry.focus()

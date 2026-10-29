
"""Typing-test state, word tracking, and score calculations."""

from create_text import CreateText


class TypingTest:
    """Manage a typing challenge independently of its graphical interface."""

    def __init__(self):
        """Initialize the paragraph generator and start a fresh test."""
        self.text_generator = CreateText()
        self.text_words: str
        self.list_words: list[str]
        self.word_starts: list[int]
        self.correct_word_list: list[str]
        self.wrong_word_list: list[str]
        self.word_index: int
        self.reset()

    def load_new_text(self) -> None:
        """Generate a fresh paragraph and rebuild the word data from it."""
        self.text_words = self.text_generator.create_text()
        self.list_words = self.text_words.split(" ")
        self.build_word_positions()

    def build_word_positions(self) -> None:
        """Calculate each word's character offset in the paragraph.

        The resulting ``word_starts`` list is used by the GUI to apply text
        highlighting. Rebuild it whenever ``list_words`` changes.
        """
        self.word_starts = []
        position = 0
        for word in self.list_words:
            self.word_starts.append(position)
            position += len(word) + 1

    def reset(self) -> None:
        """Start a new challenge and clear the previous word scores."""
        self.correct_word_list = []
        self.wrong_word_list = []
        self.word_index = 0
        self.load_new_text()

    @property
    def current_word(self) -> str:
        """Return the word currently expected from the user."""
        return self.list_words[self.word_index]

    @property
    def is_finished(self) -> bool:
        """Return whether every word in the paragraph has been submitted."""
        return self.word_index >= len(self.list_words)

    def check_word(self, raw_text: str) -> tuple[str, bool | None, str] | None:
        """Score a submitted word when the input contains a space.

        Returns:
            ``None`` if no word has been submitted. Otherwise, return
            ``(typed_word, is_correct, remainder)``. ``is_correct`` is ``None``
            for an empty submission; ``remainder`` contains text after the
            first space.
        """
        if " " not in raw_text:
            return None

        typed_word, _, remainder = raw_text.partition(" ")
        remainder = remainder.lstrip()

        # A space with no word before it: nothing to score.
        if not typed_word:
            return typed_word, None, remainder

        is_correct = typed_word == self.current_word
        if is_correct:
            self.correct_word_list.append(typed_word)
        else:
            self.wrong_word_list.append(typed_word)

        self.word_index += 1
        return typed_word, is_correct, remainder

    def accuracy(self) -> float:
        """Return the percentage of correct words among all submitted words."""
        total_words = len(self.correct_word_list) + len(self.wrong_word_list)
        if total_words == 0:
            return 0.0
        return len(self.correct_word_list) / total_words * 100

    def wpm(self, elapsed_minutes: float) -> float:
        """Return words per minute for the given elapsed time in minutes."""
        # Treat very short tests as one minute-per-60-seconds to avoid division
        # by zero and keep near-instant completion results bounded.
        elapsed_minutes = max(elapsed_minutes, 1 / 60)
        return len(self.correct_word_list) / elapsed_minutes
"""Generate sample paragraphs for typing-speed tests using Faker."""

from faker import Faker

SENTENCES_PER_TEXT = 10


class CreateText:
    """Generate the practice paragraph shown during a typing test."""

    def __init__(self):
        """Create the Faker instance used to generate paragraph text."""
        self.faker = Faker()

    def create_text(self) -> str:
        """Return a generated paragraph containing the configured sentences.

        Returns:
            The generated paragraph as a string.
        """
        return self.faker.paragraph(nb_sentences=SENTENCES_PER_TEXT)

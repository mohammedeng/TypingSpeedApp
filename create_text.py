"""Generate sample paragraphs for typing-speed tests.

The :class:`Paragraph` class wraps Faker's paragraph generator so the GUI can
request fresh practice text whenever a test starts or is reset.
"""

from faker import Faker

class Paragraph:
    """Create generated paragraph text for the typing challenge."""

    def __init__(self):
        """Initialize a Faker instance used to generate paragraphs."""
        self.faker = Faker()

    def create_paragraph(self, num_of_sentences):
        """Return a randomly generated paragraph.

        Args:
            num_of_sentences: Number of sentences to include in the paragraph.

        Returns:
            Generated paragraph text as a string.
        """
        return self.faker.paragraph(nb_sentences=num_of_sentences)

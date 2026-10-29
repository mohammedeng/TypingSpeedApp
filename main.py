"""Application entry point for the typing speed test.

Run this module directly to create the main GUI window and start its Tk event
loop. The interface and typing-test behavior are implemented in :mod:`Gui`.
"""

from Gui import Screen


def main():
    """Create the application window and run the GUI event loop."""
    screen = Screen()
    screen.mainloop()


if __name__ == "__main__":
    main()

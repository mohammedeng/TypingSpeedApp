# Typing Speed Test

A desktop typing practice app built with Python and CustomTkinter. It displays
randomly generated text, highlights typing progress, and reports words per
minute (WPM) when the timer expires or all displayed words are completed.

## Run

Python 3.10 or newer is recommended. Install the dependencies and launch the
app from the project directory:

```bash
python -m pip install customtkinter Faker
python main.py
```

Type the displayed words in order, separating each word with a space. The
duration is set in minutes (defaults to one minute). Select **Reset** to start
over with a new paragraph.

## Project modules

- `main.py` — application entry point.
- `Gui.py` — window layout, typing progress, timer, scoring, and reset behavior.
- `create_text.py` — generates practice paragraphs using Faker.

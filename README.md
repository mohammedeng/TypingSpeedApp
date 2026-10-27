# Typing Speed Test

A desktop typing practice app built with Python and CustomTkinter. It displays
randomly generated text, highlights typing progress, and reports words per
minute (WPM) when the timer expires or all displayed words are completed.

## Run

Python 3.10 or newer is recommended. Install the dependencies and launch the
app from the project directory:

```bash
python -m pip install -r requirements.txt
python main.py
```

Type the displayed words in order, separating each word with a space. The
duration is set in minutes (defaults to one minute). Select **Reset** to start
over with a new paragraph.

## Build a Windows desktop executable

The app already runs as a desktop GUI. To build a distributable Windows app
folder containing the executable and its required files, run:

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name TypingSpeedTest --collect-all customtkinter --collect-all faker --collect-all darkdetect main.py
```

After the build completes, launch `dist\TypingSpeedTest\TypingSpeedTest.exe`.
To distribute the app, share the entire `dist\TypingSpeedTest` folder, not only
the `.exe`. Build on Windows to create a Windows executable.

## Project modules

- `main.py` — application entry point.
- `Gui.py` — window layout, typing progress, timer, scoring, and reset behavior.
- `create_text.py` — generates practice paragraphs using Faker.

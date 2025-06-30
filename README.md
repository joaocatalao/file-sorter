# File Sorter

File Sorter is a desktop application written in Python with Tkinter. It allows you to create rules that automatically organize files. Each rule watches a folder and performs actions (move, copy, delete, etc.) when file patterns match your conditions.

## Features

- **Rule based** file organizing with nested condition groups.
- **Background rule engine** watches folders and runs actions in real time.
- **Polling mode** available when filesystem events are unreliable.
- **Logs tab** shows runtime messages.
- **GUI editor** implemented with Tkinter for creating and editing rules.
- **Plugin system** for custom rule types (place your Python files in `plugins/`).
- **Settings** saved to `file_sorter/data/settings.json`.
- Optional **system tray** integration using `pystray` on Windows.

## Project Structure

```
file_sorter/
    assets/      # Icons and other static assets
    config/      # Settings loading/saving
    controller/  # Application controller
    core/        # Tray manager and runtime rule engine
    data/        # User data (rules, settings)
    model/       # Rule classes and rule manager
    view/        # Tkinter UI
    main.py      # Application entry point
```

## Getting Started

1. Install Python 3 and ensure `pip` is available.
2. Install dependencies:
   ```bash
   pip install pystray pillow
   ```
3. Run the application:
   ```bash
   python file_sorter/main.py
   ```

At the first run, settings are saved under `file_sorter/data/`. Rules are stored in `file_sorter/data/rules.json` once you create them.

## License

This project is provided as-is; no specific license has been included.

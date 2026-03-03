
# prodtime
## Note: This project is vibecoded
---
`prodtime` is a cross-platform command-line productivity timer for developers.

After installation, you can run:

```bash
prodtime start
prodtime list
prodtime stats
```

from anywhere in your terminal.

---

# Requirements

* Python 3.8 or higher
* `pip` installed and available in PATH

Check:

```bash
python --version
```

or on Windows:

```bash
py --version
```

---

# Installation (All Platforms)

From the project root directory (where `pyproject.toml` is located), run:

```bash
pip install .
```

That’s it.

This installs `prodtime` globally in your current Python environment and creates a CLI executable.

---

# Windows Notes

If you're using Windows and `pip` isn’t recognized, try:

```bash
py -m pip install .
```

After installation, verify:

```bash
prodtime --help
```

If you see help output, it worked.

If the command is not found:

1. Close and reopen your terminal.
2. Ensure your Python Scripts directory is in PATH.
   Typically:

   ```
   C:\Users\YourName\AppData\Local\Programs\Python\PythonXX\Scripts\
   ```

You can check where it was installed:

```bash
where prodtime
```

---

# Ubuntu / macOS Notes

Install:

```bash
pip install .
```

or

```bash
python3 -m pip install .
```

Verify:

```bash
which prodtime
```

If installed correctly, it will show the executable path.

---

# Development Mode (Editable Install)

If you're actively modifying the project:

```bash
pip install -e .
```

This allows changes to the source code to take effect immediately without reinstalling.

---

# Data Storage

By default, `prodtime` creates:

```
timers.db
```

in the current working directory.

---

# Usage

```bash
prodtime start      # Start a timer
prodtime list       # List saved sessions
prodtime delete 3   # Delete session with ID 3
prodtime edit 2     # Edit session
prodtime stats      # View aggregated stats
prodtime export     # Export sessions to CSV
```

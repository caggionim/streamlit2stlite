# 🔦 streamlit2stlite

**Turn your Streamlit apps into standalone HTML files in seconds.**

`streamlit2stlite` is a simple tool that bundles your Streamlit application and all its dependencies into a single HTML file. This file can be opened in any modern browser, running entirely purely on the client side using WebAssembly (via [stlite](https://github.com/whitphx/stlite)). **No server, no hosting costs, no deployment headaches.**

> 💡 Perfect for sharing data dashboards, prototypes, and tools with colleagues or clients who don't have Python installed.

## 🎮 Try it now!

Don't want to install anything yet? specific files are included in this repository that you can download and run immediately:

*   **[Converter Tool](converter_app.html)** (`converter_app.html`): A self-contained tool that lets you upload and convert other Streamlit apps to HTML directly in your browser.
*   **[Example App](example_app.html)** (`example_app.html`): A simple demo showing what the output looks like.

**To use them:**
1.  Click the link above (or navigate to the file in the repo).
2.  Download the raw file (on GitHub, click "Download raw file" button).
3.  Open the downloaded `.html` file in Chrome, Edge, or Firefox.

## 🚀 Quick Start

1.  **Install** the tool:
    ```bash
    pip install streamlit2stlite
    ```

2.  **Convert** your app:
    ```bash
    streamlit2stlite my_app.py
    ```

3.  **Open** `my_app.html` in your browser. That's it!

---

## ✨ Features

*   **📦 Auto-Magic Dependency Detection**: Automatically scans your imports to determine which packages to install in the browser (e.g., proper handling of `pandas`, `numpy`, `scipy` for `lmfit`, etc.).
*   **� LaTeX Support**: Correctly handles backslashes in your math equations so they render perfectly.
*   **�️ Smart Titles**: Automatically detects your app's title from `st.set_page_config()` or `st.title()`.
*   **🛠️ Full Control**: Override requirements, titles, or the stlite version via CLI flags if you need to.

## � Usage Guide

### Basic Conversion
The simplest way to use it. Defaults to creating an HTML file with the same name as your script.

```bash
streamlit2stlite dashboard.py
# -> Creates dashboard.html
```

### Custom Output Name
Specify exactly where you want the file to go.

```bash
streamlit2stlite script.py -o ./dist/awesome_dashboard.html
```

### Managing Dependencies
We try to guess your dependencies, but sometimes you need to be specific.

**Add extra packages:**
```bash
streamlit2stlite app.py --add-requirements "scikit-learn,purple-air"
```

**Override completely:**
```bash
streamlit2stlite app.py --requirements "streamlit,pandas,numpy"
```

### Full CLI Options

```text
usage: streamlit2stlite [-h] [-o OUTPUT] [-r REQUIREMENTS] [-t TITLE]
                        [--stlite-version STLITE_VERSION]
                        [--add-requirements ADD_REQUIREMENTS] [-v]
                        input

positional arguments:
  input                 Path to the input Streamlit Python file

options:
  -h, --help            show this help message
  -o, --output          Path to the output HTML file
  -r, --requirements    Comma-separated list of packages to install
  -t, --title           Title for the HTML page
  --add-requirements    Additional packages to add to auto-detected ones
  -v, --verbose         Print verbose output
## ⚠️ Limitations

While running Python in the browser is magical, it has some constraints you should be aware of:

*   **Library Support**: You can only use:
    *   **Pure Python** packages found on PyPI (packages that don't require C compilation).
    *   **Scientific packages** expressly ported to Pyodide (e.g., `numpy`, `pandas`, `scipy`, `matplotlib`, `scikit-learn`).
    *   *System-level* packages like `opencv-python` (cv2) or complex compiled libraries that haven't been ported will **NOT** work.
*   **Performance**: Code runs in the browser, so it's generally slower than native Python. Heavy data processing might lag the UI.
*   **Networking**: Standard `requests` won't work due to browser CORS security. You must use `pyodide.http` or libraries that wrap the browser's `fetch` API.
*   **File System**: No direct access to the user's local hard drive. Use `st.file_uploader` and `st.download_button` to interact with files.

## ❓ FAQ

**How does this work?**
It embeds your Python code into a template that loads `stlite` (a port of Streamlit to WebAssembly). When you open the HTML file, your browser downloads a mini Python environment (Pyodide) and runs your code locally.

**Can I read local files?**
Because this runs in the browser, it cannot read files from your hard drive directly (sandbox security). You should use `st.file_uploader` to let users provide files, or embed data directly into your script.

**Does it support all Python packages?**
It supports packages available in [Pyodide](https://pyodide.org/en/stable/usage/packages-in-pyodide.html) (including numpy, pandas, scipy, matplotlib, scikit-learn) and pure Python packages from PyPI (micropip).

## 📄 License

MIT License. Feel free to use this for whatever you want!

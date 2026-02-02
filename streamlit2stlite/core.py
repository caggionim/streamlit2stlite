import re
from typing import Optional, List, Set, Union

# Default stlite version
STLITE_VERSION = "1.0.0"

# HTML template header
HTML_HEADER = '''<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />
    <title>{title}</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@{stlite_version}/build/stlite.css"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module">
      import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@{stlite_version}/build/stlite.js";

      // The Streamlit application code is defined here
      const streamlit_app_code = `'''

# HTML template footer
HTML_FOOTER = '''`;
      // Mount the stlite app with the specified requirements and files
      mount(
        {{
          requirements: [{requirements}], // Packages to install
          entrypoint: "streamlit_app.py", // This field is required
          files: {{
            "streamlit_app.py": streamlit_app_code,
          }},
        }},
        document.getElementById("root"),
      );
    </script>
  </body>
</html>
'''


def escape_for_js_template_literal(python_code: str) -> str:
    r"""
    Escape Python code for embedding in a JavaScript template literal.
    
    Key transformations:
    1. Escape backticks (`) as they delimit template literals
    2. Escape ${} sequences as they are template literal interpolation
    3. Escape backslashes properly for JavaScript template literals
    
    In Python source code:
    - `\sigma` in source = literal `\sigma` when read
    - For JS template literal, we need `\\sigma` to represent `\sigma`
    
    So when reading a Python file:
    - Single backslash in the read content needs to become double backslash in JS
    
    Args:
        python_code: The raw Python code to escape
        
    Returns:
        Escaped Python code safe for JS template literal embedding
    """
    # First, escape all backslashes for JavaScript template literal
    # A single backslash in the content needs to be \\ in JS template literal
    escaped = python_code.replace('\\', '\\\\')
    
    # Escape backticks with backslash (they delimit template literals)
    escaped = escaped.replace('`', '\\`')
    
    # Escape template literal interpolation sequences
    escaped = escaped.replace('${', '\\${')
    
    return escaped


def extract_imports(python_code: str) -> List[str]:
    """
    Extract imported packages from Python code to suggest requirements.
    
    Args:
        python_code: The Python source code
        
    Returns:
        List of package names that should be installed
    """
    packages: Set[str] = set()
    
    # Common import patterns - extract the top-level package name
    # Handles: import pkg, import pkg.submodule, from pkg import ..., from pkg.sub import ...
    import_patterns = [
        r'^import\s+([\w]+)',              # import package or import package.submodule
        r'^from\s+([\w]+)(?:\.\w+)*\s+import',  # from package.submodule import ...
    ]
    
    for line in python_code.split('\n'):
        line = line.strip()
        for pattern in import_patterns:
            match = re.match(pattern, line)
            if match:
                pkg = match.group(1)
                # Map common module names to pip package names
                pkg_mapping = {
                    'cv2': 'opencv-python',
                    'sklearn': 'scikit-learn',
                    'PIL': 'Pillow',
                    'yaml': 'pyyaml',
                    'bs4': 'beautifulsoup4',
                }
                packages.add(pkg_mapping.get(pkg, pkg))
    
    # Remove standard library modules that don't need installation
    stdlib = {
        'os', 'sys', 're', 'json', 'datetime', 'time', 'math', 'random',
        'collections', 'itertools', 'functools', 'operator', 'copy',
        'io', 'base64', 'hashlib', 'pickle', 'pathlib', 'typing',
        'abc', 'contextlib', 'dataclasses', 'enum', 'warnings',
        'threading', 'multiprocessing', 'subprocess', 'socket',
        'urllib', 'http', 'email', 'html', 'xml', 'csv', 'sqlite3',
        'logging', 'unittest', 'doctest', 'pdb', 'traceback',
        'gc', 'inspect', 'importlib', 'pkgutil', 'platform',
        'struct', 'array', 'decimal', 'fractions', 'statistics',
        'tempfile', 'shutil', 'glob', 'fnmatch', 'linecache',
        'textwrap', 'difflib', 'string', 'secrets', 'uuid',
        'argparse', 'getopt', 'configparser', 'fileinput',
        'stat', 'filecmp', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma',
        'zlib', 'binascii', 'quopri', 'uu', 'codecs',
    }
    
    # Also remove streamlit since it's built into stlite
    stdlib.add('streamlit')
    stdlib.add('st')
    
    packages = packages - stdlib
    
    # Add common dependencies that aren't directly imported but are needed
    # These are dependencies of commonly used packages
    dependency_additions = {
        'lmfit': ['scipy'],           # lmfit needs scipy
        'tadatakit': ['pydantic'],    # tadatakit needs pydantic
        'plotly': [],
        'pandas': ['xlsxwriter', 'openpyxl'],
        'numpy': [],
        'matplotlib': [],
    }
    
    for pkg in list(packages):
        if pkg in dependency_additions:
            packages.update(dependency_additions[pkg])
    
    return sorted(list(packages))


def detect_title_from_code(python_code: str) -> str:
    """
    Try to detect the app title from st.set_page_config or st.title calls.
    
    Args:
        python_code: The Python source code
        
    Returns:
        Detected title or default
    """
    # Look for page_title in set_page_config
    match = re.search(r'page_title\s*=\s*["\']([^"\']+)["\']', python_code)
    if match:
        return match.group(1)
    
    # Look for st.title
    match = re.search(r'st\.title\s*\(\s*["\']([^"\']+)["\']', python_code)
    if match:
        # Remove emoji prefixes if present
        title = match.group(1)
        # Clean up emoji at the start
        title = re.sub(r'^[^\w\s]+\s*', '', title)
        return title if title else "Streamlit App"
    
    return "Streamlit App"


def convert_streamlit_to_stlite(
    python_code: str,
    title: Optional[str] = None,
    requirements: Optional[List[str]] = None,
    stlite_version: str = STLITE_VERSION
) -> str:
    """
    Convert a Streamlit Python app to an stlite HTML app.
    
    Args:
        python_code: The Streamlit Python source code
        title: Optional title for the HTML page
        requirements: Optional list of pip packages to install
        stlite_version: Version of stlite to use
        
    Returns:
        Complete HTML document with embedded stlite app
    """
    # Detect title if not provided
    if title is None:
        title = detect_title_from_code(python_code)
    
    # Detect requirements if not provided
    if requirements is None:
        requirements = extract_imports(python_code)
    
    # Escape the Python code for JavaScript template literal
    escaped_code = escape_for_js_template_literal(python_code)
    
    # Format requirements as JavaScript array elements
    req_str = ', '.join(f'"{pkg}"' for pkg in requirements)
    
    # Build the HTML document
    header = HTML_HEADER.format(
        title=title,
        stlite_version=stlite_version
    )
    
    footer = HTML_FOOTER.format(
        requirements=req_str
    )
    
    return header + escaped_code + footer

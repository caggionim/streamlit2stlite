import pytest
from streamlit2stlite.core import (
    escape_for_js_template_literal,
    extract_imports,
    detect_title_from_code,
    convert_streamlit_to_stlite
)

def test_escape_for_js_template_literal():
    # Test backslash escaping
    code = r"print('Hello \n World')"
    escaped = escape_for_js_template_literal(code)
    # The result should have double backslashes for the newline char representation in Python string
    # But effectively passing \\ to JS.
    # In python string literal r"\\" is actually \
    assert r"\\" in escaped 
    
    # Test backtick escaping
    code = "print(f`Hello`)"
    escaped = escape_for_js_template_literal(code)
    assert r"\`" in escaped

    # Test template interpolation escaping
    code = "const x = `${variable}`"
    escaped = escape_for_js_template_literal(code)
    assert r"\${" in escaped
    
    # Combined test
    code = r"path = 'c:\users\name'"
    # Expected: c:\\users\\name in the JS string
    escaped = escape_for_js_template_literal(code)
    assert r"\\" in escaped

def test_extract_imports():
    code = """
import pandas as pd
import numpy
from plotly import express
import cv2
import os
import sys
"""
    reqs = extract_imports(code)
    
    # Check that standard lib is ignored
    assert "os" not in reqs
    assert "sys" not in reqs
    
    # Check simple imports
    assert "pandas" in reqs
    assert "numpy" in reqs
    
    # Check from imports
    assert "plotly" in reqs
    
    # Check mapping
    assert "opencv-python" in reqs
    assert "cv2" not in reqs

def test_extract_imports_dependencies():
    code = "import lmfit"
    reqs = extract_imports(code)
    assert "lmfit" in reqs
    assert "scipy" in reqs # lmfit dependency

    # Test pandas -> xlsxwriter
    code_pandas = "import pandas"
    reqs_pandas = extract_imports(code_pandas)
    assert "pandas" in reqs_pandas
    assert "xlsxwriter" in reqs_pandas

def test_detect_title_from_code():
    # Test set_page_config
    code1 = """
import streamlit as st
st.set_page_config(page_title="My Cool App")
"""
    assert detect_title_from_code(code1) == "My Cool App"

    # Test st.title
    code2 = """
import streamlit as st
st.title("My Title")
"""
    assert detect_title_from_code(code2) == "My Title"
    
    # Test emoji cleanup
    code3 = """
st.title("🚀 Blast Off")
"""
    assert detect_title_from_code(code3) == "Blast Off"
    
    # Test default
    code4 = "print('hello')"
    assert detect_title_from_code(code4) == "Streamlit App"

def test_convert_streamlit_to_stlite():
    code = "import streamlit as st\nst.write('Hello')"
    html = convert_streamlit_to_stlite(code, title="Test App")
    
    assert "<!doctype html>" in html
    assert "<title>Test App</title>" in html
    assert "stlite.js" in html
    assert "stlite.css" in html
    assert "streamlit_app_code = `" in html
    assert "mount(" in html
    
    # Check that code is present
    assert "st.write('Hello')" in html

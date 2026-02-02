import streamlit as st
from streamlit2stlite.core import convert_streamlit_to_stlite, extract_imports

st.set_page_config(page_title="Streamlit to Stlite Converter", page_icon="⚡", layout="wide")

st.title("⚡ Streamlit to Stlite Converter")
st.markdown("""
### 🚀 Turn your Streamlit apps into standalone HTML files!

Upload your Streamlit Python file (`.py`) below to convert it into a single HTML file powered by [stlite](https://github.com/whitphx/stlite).
No server required - just open the file in your browser! 🌐
""")

uploaded_file = st.file_uploader("📂 Upload your Streamlit App (.py)", type=["py"])

if uploaded_file is not None:
    # Read the file content
    python_code = uploaded_file.getvalue().decode("utf-8")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Source Code")
        st.code(python_code, language="python")
        
    with col2:
        st.subheader("⚙️ Configuration")
        
        # Auto-detect title
        title = st.text_input("🏷️ App Title", value="My Stlite App")
        
        # Requirements
        detected_reqs = extract_imports(python_code)
        if detected_reqs:
             st.info(f"📦 Auto-detected requirements: `{', '.join(detected_reqs)}`")
        else:
             st.info("📦 No external requirements detected.")
        
        # Allow user to modify requirements
        requirements_str = st.text_area(
            "📚 Requirements (comma-separated)", 
            value=", ".join(detected_reqs),
            help="List of pip packages to install (e.g., pandas, numpy)."
        )
        
        requirements = [r.strip() for r in requirements_str.split(",") if r.strip()]
        
        st.divider()
        
        if st.button("✨ Convert to HTML", type="primary"):
            try:
                html_content = convert_streamlit_to_stlite(
                    python_code=python_code,
                    title=title,
                    requirements=requirements
                )
                
                st.success("🎉 Conversion successful! Your app is ready.")
                
                # Determine filename
                file_name_download = uploaded_file.name.replace(".py", ".html")
                
                # Create download button
                st.download_button(
                    label="📥 Download HTML File",
                    data=html_content,
                    file_name=file_name_download,
                    mime="text/html"
                )
            except Exception as e:
                st.error(f"🚨 An error occurred during conversion: {e}")

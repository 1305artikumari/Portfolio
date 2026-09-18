import base64
from pathlib import Path
import re
import streamlit as st
import streamlit.components.v1 as components

# Set Streamlit page configuration
st.set_page_config(
    page_title="Arti Kumari — Data Analyst & Data Scientist | Kantar",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit header, footer, toolbar, padding and force full-screen iframe
st.markdown(
    """
    <style>
    /* Hide all default Streamlit UI wrappers */
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    html, body, .stApp {
        background-color: #080a12 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        height: 100vh !important;
        width: 100vw !important;
    }
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    div[data-testid="stVerticalBlock"], div[data-testid="element-container"] {
        gap: 0 !important;
        height: 100vh !important;
        width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        z-index: 999999 !important;
        display: block !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent


def build_portfolio_page() -> str:
    html_path = BASE_DIR / "index.html"
    css_path = BASE_DIR / "css" / "styles.css"
    js_path = BASE_DIR / "js" / "main.js"
    photo_path = BASE_DIR / "assets" / "arti-photo.jpg"
    resume_path = BASE_DIR / "assets" / "Arti_Resume.pdf"

    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

    # Ensure HTML and body inside iframe allow smooth full-page scrolling
    iframe_helper_css = """
    <style>
      html, body {
        height: 100%;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch;
        scroll-behavior: smooth;
      }
      body {
        min-height: 100vh;
      }
    </style>
    """

    # Inline CSS
    html = re.sub(
        r'<link\s+rel=["\']stylesheet["\']\s+href=["\']css/styles\.css["\']\s*/?>',
        f"<style>\n{css}\n</style>",
        html,
        flags=re.IGNORECASE,
    )

    # Inline JavaScript
    html = re.sub(
        r'<script\s+src=["\']js/main\.js["\']\s*></script>',
        f"<script>\n{js}\n</script>",
        html,
        flags=re.IGNORECASE,
    )

    # Inline photo base64
    if photo_path.exists():
        photo_b64 = base64.b64encode(photo_path.read_bytes()).decode("utf-8")
        html = html.replace('assets/arti-photo.jpg', f'data:image/jpeg;base64,{photo_b64}')

    # Inline resume PDF base64
    if resume_path.exists():
        pdf_b64 = base64.b64encode(resume_path.read_bytes()).decode("utf-8")
        html = html.replace(
            'href="assets/Arti_Resume.pdf"',
            f'href="data:application/pdf;base64,{pdf_b64}" download="Arti_Resume.pdf"',
        )

    # Inject iframe helper styling in head
    if "</head>" in html:
        html = html.replace("</head>", f"{iframe_helper_css}\n</head>")
    else:
        html = iframe_helper_css + html

    return html


# Render the complete self-contained portfolio webpage
components.html(build_portfolio_page(), scrolling=True)

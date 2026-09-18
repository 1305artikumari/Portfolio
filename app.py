import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Arti Kumari — Data Analyst & Data Scientist | Kantar",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlit clean viewport override
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    .stApp [data-testid="stToolbar"] {display: none;}
    .stApp [data-testid="stDecoration"] {display: none;}
    .stApp [data-testid="stHeader"] {display: none;}
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        display: block !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent


def load_portfolio_html() -> str:
    html_path = BASE_DIR / "index.html"
    css_path = BASE_DIR / "css" / "styles.css"
    js_path = BASE_DIR / "js" / "main.js"
    photo_path = BASE_DIR / "assets" / "arti-photo.jpg"
    resume_path = BASE_DIR / "assets" / "Arti_Resume.pdf"

    html_content = html_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    js_content = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

    # Embed CSS
    html_content = html_content.replace(
        '<link rel="stylesheet" href="css/styles.css" />',
        f"<style>\n{css_content}\n</style>",
    )
    html_content = html_content.replace(
        '<link rel="stylesheet" href="css/styles.css">',
        f"<style>\n{css_content}\n</style>",
    )

    # Embed JS
    html_content = html_content.replace(
        '<script src="js/main.js"></script>',
        f"<script>\n{js_content}\n</script>",
    )

    # Embed Photo Base64
    if photo_path.exists():
        photo_b64 = base64.b64encode(photo_path.read_bytes()).decode("utf-8")
        html_content = html_content.replace(
            'src="assets/arti-photo.jpg"',
            f'src="data:image/jpeg;base64,{photo_b64}"',
        )
        html_content = html_content.replace(
            "src='assets/arti-photo.jpg'",
            f"src='data:image/jpeg;base64,{photo_b64}'",
        )

    # Embed Resume Base64
    if resume_path.exists():
        pdf_b64 = base64.b64encode(resume_path.read_bytes()).decode("utf-8")
        html_content = html_content.replace(
            'href="assets/Arti_Resume.pdf"',
            f'href="data:application/pdf;base64,{pdf_b64}" download="Arti_Resume.pdf"',
        )
        html_content = html_content.replace(
            "href='assets/Arti_Resume.pdf'",
            f"href='data:application/pdf;base64,{pdf_b64}' download='Arti_Resume.pdf'",
        )

    # Embed dynamic frame height communicator
    auto_resize_script = """
    <script>
      function sendHeight() {
        const height = Math.max(
          document.body.scrollHeight,
          document.documentElement.scrollHeight,
          document.body.offsetHeight,
          document.documentElement.offsetHeight,
          document.body.clientHeight,
          document.documentElement.clientHeight
        );
        window.parent.postMessage({ type: 'streamlit:setFrameHeight', height: height }, '*');
      }
      window.addEventListener('load', sendHeight);
      window.addEventListener('resize', sendHeight);
      setTimeout(sendHeight, 400);
      setTimeout(sendHeight, 1000);
      setTimeout(sendHeight, 2500);
    </script>
    """
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{auto_resize_script}\n</body>")
    else:
        html_content += auto_resize_script

    return html_content


portfolio_html = load_portfolio_html()
components.html(portfolio_html, height=5200, scrolling=False)

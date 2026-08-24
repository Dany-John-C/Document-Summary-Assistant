"""
Document Summary Assistant
A Streamlit app that extracts text from PDFs and images, then generates smart summaries using Groq API.
"""

import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import io
import os
import re
from groq import Groq

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Summary Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Import Google Font */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* Global reset */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Dark gradient background */
  .stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
    min-height: 100vh;
  }

  /* Hero header */
  .hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
  }
  .hero-header h1 {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  .hero-header p {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 300;
  }

  /* Glass card */
  .glass-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.8rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
  }

  /* Summary output box */
  .summary-box {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(96, 165, 250, 0.08));
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 14px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #e2e8f0;
    line-height: 1.75;
    font-size: 0.97rem;
  }

  /* Key points */
  .keypoints-box {
    background: linear-gradient(135deg, rgba(52, 211, 153, 0.08), rgba(16, 185, 129, 0.05));
    border: 1px solid rgba(52, 211, 153, 0.25);
    border-radius: 14px;
    padding: 1.5rem;
    margin: 1rem 0;
  }
  .keypoints-box h4 {
    color: #34d399;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
  }
  .keypoints-box ul {
    color: #cbd5e1;
    line-height: 1.8;
    padding-left: 1.2rem;
    margin: 0;
  }

  /* Section labels */
  .section-label {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.4rem;
  }

  /* Stat badge */
  .stat-badge {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.3);
    color: #a78bfa;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }

  /* Sidebar styling */
  [data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
  }
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {
    color: #a78bfa !important;
  }

  /* File uploader zone */
  [data-testid="stFileUploaderDropzone"] {
    background: rgba(124, 58, 237, 0.06) !important;
    border: 2px dashed rgba(167, 139, 250, 0.4) !important;
    border-radius: 12px !important;
  }

  /* Primary button */
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s ease !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
  }

  /* Download button */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }

  /* Spinner override */
  .stSpinner > div {
    border-top-color: #7c3aed !important;
  }

  /* Info / warning boxes */
  .stAlert {
    border-radius: 10px !important;
  }

  /* Radio buttons */
  .stRadio > label {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
  }

  /* Sidebar text inputs */
  .stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
  }

  /* Hide Streamlit branding */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber."""
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"[Page {i+1}]\n{page_text.strip()}")
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")
    
    if not text_parts:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned/image-based PDF — try saving it as an image and uploading again."
        )
    return "\n\n".join(text_parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract OCR."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB if needed (handles RGBA, palette mode, etc.)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image, config="--psm 6")
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")
    
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("No text could be extracted from this image. Ensure it contains readable printed text.")
    return cleaned


def clean_text(text: str, max_chars: int = 12000) -> str:
    """Clean and truncate extracted text for the prompt."""
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    # Truncate to avoid token limits (keep first max_chars chars)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... document truncated for summary ...]"
    return text.strip()


def build_prompt(text: str, length: str) -> str:
    """Build the summarization prompt based on selected length."""
    length_instructions = {
        "Short": (
            "Provide a concise summary in 2–3 sentences (≈60–80 words). "
            "Capture only the absolute core message."
        ),
        "Medium": (
            "Provide a clear summary in 1–2 short paragraphs (≈150–200 words). "
            "Cover the main topics and most important details."
        ),
        "Long": (
            "Provide a comprehensive summary in 3–5 paragraphs (≈350–500 words). "
            "Cover all major sections, arguments, and details thoroughly."
        ),
    }
    instruction = length_instructions.get(length, length_instructions["Medium"])
    return f"""You are a professional document analyst. Analyze the document below and respond with the following two-part structure:

**SUMMARY:**
{instruction}

**KEY POINTS:**
List exactly 5 bullet points (start each with "•") highlighting the most important facts, findings, or takeaways from the document.

Do not add any other headers or sections. Be factual and precise.

---
DOCUMENT TEXT:
{text}
"""


def generate_summary(api_key: str, text: str, length: str) -> tuple[str, str]:
    """
    Call Groq API and return (summary_text, key_points_text).
    Raises RuntimeError on API failure.
    """
    client = Groq(api_key=api_key)
    prompt = build_prompt(text, length)

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise, professional document summarizer. "
                        "Always follow the exact output format requested."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error: {e}")

    raw = response.choices[0].message.content.strip()

    # Parse summary and key points from response
    summary, key_points = "", ""
    if "**SUMMARY:**" in raw and "**KEY POINTS:**" in raw:
        parts = raw.split("**KEY POINTS:**")
        summary = parts[0].replace("**SUMMARY:**", "").strip()
        key_points = parts[1].strip()
    elif "KEY POINTS:" in raw and "SUMMARY:" in raw:
        parts = raw.split("KEY POINTS:")
        summary = parts[0].replace("SUMMARY:", "").strip()
        key_points = parts[1].strip()
    else:
        # Fallback: treat whole response as summary
        summary = raw
        key_points = ""

    return summary, key_points


def format_key_points_html(key_points_raw: str) -> str:
    """Convert bullet text to an HTML unordered list."""
    lines = [l.strip() for l in key_points_raw.splitlines() if l.strip()]
    items = []
    for line in lines:
        # Strip leading bullets / dashes / numbers
        clean = re.sub(r"^[•\-\*\d\.]+\s*", "", line).strip()
        if clean:
            items.append(f"<li>{clean}</li>")
    if not items:
        return key_points_raw
    return "<ul>" + "".join(items) + "</ul>"


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    # Check if API key is stored in Streamlit Secrets, otherwise show input
    if "GROQ_API_KEY" in st.secrets:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    else:
        groq_api_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your free API key at https://console.groq.com",
        )
        if not groq_api_key:
            st.info("👆 Enter your free Groq API key to enable summarization.", icon="ℹ️")

    st.markdown("---")
    st.markdown("## 📏 Summary Length")
    summary_length = st.radio(
        "Choose summary length:",
        options=["Short", "Medium", "Long"],
        index=1,
        help="Short: ~80 words | Medium: ~175 words | Long: ~400 words",
    )

    st.markdown("---")
    st.markdown("## ℹ️ About")
    st.markdown(
        """
        **Document Summary Assistant** extracts text from PDFs and images, 
        then uses Groq's LLM API (Llama 3) to generate intelligent summaries.
        
        **Supported formats:**
        - 📄 PDF (`.pdf`)
        - 🖼️ Images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.webp`)
        
        **Stack:** Streamlit · pdfplumber · pytesseract · Groq (Llama 3)
        """
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#475569; font-size:0.78rem;'>"
        "Built for Unthinkable Solutions Technical Assessment"
        "</div>",
        unsafe_allow_html=True,
    )


# ─── Hero Header ──────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero-header'>
  <h1>📄 Document Summary Assistant</h1>
  <p>Upload any PDF or image — get an instant, AI-powered smart summary</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Upload Section ───────────────────────────────────────────────────────────

col_upload, col_info = st.columns([3, 2], gap="large")

with col_upload:
    st.markdown("<div class='section-label'>Upload Document</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag & drop or click to browse",
        type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        label_visibility="collapsed",
    )

with col_info:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🚀 How it works")
    st.markdown("""
1. **Upload** a PDF or image document  
2. **Choose** your preferred summary length  
3. **Enter** your free Groq API key in the sidebar  
4. **Click** Generate Summary  
5. **Download** your summary as a text file  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Main Processing ──────────────────────────────────────────────────────────

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_size_kb = len(file_bytes) / 1024
    file_ext = file_name.rsplit(".", 1)[-1].lower()

    st.markdown("---")
    # File metadata badges
    st.markdown(
        f"<span class='stat-badge'>📁 {file_name}</span>"
        f"<span class='stat-badge'>📦 {file_size_kb:.1f} KB</span>"
        f"<span class='stat-badge'>🏷️ {file_ext.upper()}</span>"
        f"<span class='stat-badge'>📏 {summary_length} summary</span>",
        unsafe_allow_html=True,
    )

    # ── Image preview (for image files) ──────────────────────────────────────
    if file_ext in ("png", "jpg", "jpeg", "bmp", "tiff", "webp"):
        try:
            preview_img = Image.open(io.BytesIO(file_bytes))
            # Limit preview size
            preview_img.thumbnail((400, 400))
            col_prev, _ = st.columns([1, 2])
            with col_prev:
                st.image(preview_img, caption="Uploaded Image Preview", use_container_width=True)
        except Exception:
            pass  # Skip preview on failure

    st.markdown("---")

    generate_btn = st.button("✨ Generate Summary", use_container_width=True)

    if generate_btn:
        # ── Validate API key ─────────────────────────────────────────────────
        if not groq_api_key or not groq_api_key.strip().startswith("gsk_"):
            st.error("⚠️ Please enter a valid Groq API key in the sidebar (starts with `gsk_`).")
            st.stop()

        # ── Step 1: Extract text ─────────────────────────────────────────────
        extracted_text = ""
        with st.spinner("🔍 Extracting text from document..."):
            try:
                if file_ext == "pdf":
                    extracted_text = extract_text_from_pdf(file_bytes)
                else:
                    extracted_text = extract_text_from_image(file_bytes)
            except (ValueError, RuntimeError) as e:
                st.error(f"❌ Text Extraction Failed: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Unexpected error during text extraction: {e}")
                st.stop()

        word_count = len(extracted_text.split())
        char_count = len(extracted_text)

        # ── Step 2: Generate summary ─────────────────────────────────────────
        cleaned = clean_text(extracted_text)
        summary_text, key_points_text = "", ""

        with st.spinner("🤖 Generating AI summary via Groq (Llama 3)..."):
            try:
                summary_text, key_points_text = generate_summary(
                    groq_api_key.strip(), cleaned, summary_length
                )
            except RuntimeError as e:
                st.error(f"❌ Summarization Failed: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Unexpected error during summarization: {e}")
                st.stop()

        # ── Step 3: Display results ───────────────────────────────────────────
        st.success("✅ Summary generated successfully!")

        st.markdown(
            f"<span class='stat-badge'>📝 {word_count:,} words extracted</span>"
            f"<span class='stat-badge'>🔤 {char_count:,} characters</span>",
            unsafe_allow_html=True,
        )

        tab_summary, tab_points, tab_raw = st.tabs(
            ["📋 Summary", "🎯 Key Points", "🔍 Extracted Text"]
        )

        with tab_summary:
            st.markdown("<div class='section-label'>AI-Generated Summary</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='summary-box'>{summary_text}</div>", unsafe_allow_html=True)

        with tab_points:
            if key_points_text:
                st.markdown("<div class='section-label'>Key Takeaways</div>", unsafe_allow_html=True)
                html_points = format_key_points_html(key_points_text)
                st.markdown(
                    f"<div class='keypoints-box'><h4>🎯 Key Points</h4>{html_points}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("Key points were not parsed separately. Check the Summary tab for complete output.")

        with tab_raw:
            st.markdown("<div class='section-label'>Extracted Raw Text</div>", unsafe_allow_html=True)
            st.text_area(
                "Extracted text (read-only)",
                value=extracted_text,
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

        # ── Download button ───────────────────────────────────────────────────
        download_content = (
            f"DOCUMENT SUMMARY ASSISTANT — OUTPUT\n"
            f"{'='*50}\n\n"
            f"File: {file_name}\n"
            f"Summary Length: {summary_length}\n"
            f"Words Extracted: {word_count:,}\n\n"
            f"{'='*50}\n"
            f"SUMMARY\n"
            f"{'='*50}\n\n"
            f"{summary_text}\n\n"
            f"{'='*50}\n"
            f"KEY POINTS\n"
            f"{'='*50}\n\n"
            f"{key_points_text}\n"
        )

        st.download_button(
            label="⬇️ Download Summary as .txt",
            data=download_content.encode("utf-8"),
            file_name=f"summary_{file_name.rsplit('.', 1)[0]}.txt",
            mime="text/plain",
            use_container_width=True,
        )

else:
    # ── Empty state placeholder ───────────────────────────────────────────────
    st.markdown(
        """
        <div class='glass-card' style='text-align:center; padding: 3rem 2rem;'>
          <div style='font-size:4rem; margin-bottom:1rem;'>📂</div>
          <h3 style='color:#94a3b8; font-weight:500;'>No document uploaded yet</h3>
          <p style='color:#64748b; font-size:0.95rem;'>
            Upload a PDF or image above to get started.<br>
            Supported: PDF, PNG, JPG, JPEG, BMP, TIFF, WEBP
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

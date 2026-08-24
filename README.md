# 📄 Document Summary Assistant

> An intelligent document analysis tool that extracts text from PDFs and scanned images, then generates smart AI-powered summaries using the Groq API (Llama 3).

🔗 **Live App:** _[Add your Streamlit Community Cloud URL here after deployment]_

---

## ✨ Features

| Feature | Details |
|---|---|
| **Document Upload** | Drag-and-drop or file-picker for PDF & image files |
| **PDF Text Extraction** | `pdfplumber` — extracts text while preserving layout |
| **OCR for Images** | `pytesseract` (Tesseract engine) for scanned documents |
| **AI Summarization** | Groq API · Llama 3 (8B) · fast, free-tier |
| **Summary Lengths** | Short (~80 words), Medium (~175 words), Long (~400 words) |
| **Key Points** | Automatically extracts 5 structured bullet-point takeaways |
| **Download** | Export summary + key points as a `.txt` file |
| **Responsive UI** | Mobile-friendly Streamlit layout with dark glassmorphism theme |

---

## 🛠️ Tech Stack

- **Framework:** [Streamlit](https://streamlit.io/)
- **PDF Parsing:** [pdfplumber](https://github.com/jsvine/pdfplumber)
- **OCR:** [pytesseract](https://github.com/madmaze/pytesseract) + [Tesseract](https://github.com/tesseract-ocr/tesseract)
- **AI Summarization:** [Groq API](https://console.groq.com) · `llama3-8b-8192` model
- **Image Processing:** [Pillow](https://pillow.readthedocs.io/)

---

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system
  - **Windows:** [Download installer](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
  - **macOS:** `brew install tesseract`
  - **Linux:** `sudo apt install tesseract-ocr`
- A free [Groq API key](https://console.groq.com) (no credit card required)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Dany-John-C/Document-Summary-Assistant.git
cd Document-Summary-Assistant

# 2. Create a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

### Usage

1. Open the app (default: `http://localhost:8501`)
2. Paste your **Groq API key** in the sidebar (`gsk_...`)
3. Upload a **PDF** or **image** file using the uploader
4. Choose your preferred **summary length** (Short / Medium / Long)
5. Click **✨ Generate Summary**
6. View the summary, key points, and extracted raw text in the tabbed output
7. Download the results as a `.txt` file

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Fork / push this repo to GitHub (public, `main` branch)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repo → set `app.py` as the main file
4. Add `GROQ_API_KEY` as a secret in **Advanced settings** (optional — users can also enter it in the UI)
5. Click **Deploy** — your app will be live in ~2 minutes

---

## 📁 Project Structure

```
Document-Summary-Assistant/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 📝 Approach (200-word write-up)

The Document Summary Assistant solves the challenge of quickly digesting large documents by combining classical NLP extraction techniques with modern LLM summarization.

**Text Extraction:** For PDFs, I use `pdfplumber`, which reliably extracts text while preserving multi-column layouts and page structure. For image-based or scanned documents, `pytesseract` wraps Google's Tesseract OCR engine to convert pixel data into machine-readable text. Both paths include robust error handling — corrupt files, empty pages, and unreadable images are caught gracefully with user-friendly messages.

**Summarization:** Extracted text is cleaned (whitespace normalization, truncation to ~12,000 characters to stay within token limits) and sent to Groq's API running `llama3-8b-8192`. The model is prompted with a structured format that separates the narrative summary from bullet-point key takeaways. Summary length is controlled via three preset prompt instructions (short/medium/long), giving users flexibility without complexity.

**UX:** The entire app lives in a single `app.py` file using Streamlit, which handles file upload, UI rendering, and backend logic seamlessly. The API key is entered at runtime via a password input — keeping it out of the codebase entirely, which is critical for a public repository.

---

## 📋 Submission Checklist

- [x] App runs without errors
- [x] PDF text extraction works
- [x] Image OCR works
- [x] Short / Medium / Long summary lengths
- [x] Key points highlighted separately
- [x] Download summary feature
- [x] Error handling & loading states
- [x] No `.env`, `node_modules`, or build artifacts committed
- [x] Branch: `main`, public repository
- [x] README with setup & approach write-up

---

## 📄 License

MIT License — free to use, modify, and distribute.

# ⬡ DocMind — Multi-PDF Q&A System

An AI-powered document intelligence tool that lets you upload multiple PDFs and ask questions about their contents. Built with LangChain, Google Gemini, FAISS, and Streamlit.

---

## How It Works

```
PDFs → Text Extraction → Chunking → Embeddings → FAISS Index
                                                       ↓
Answer ← Gemini 1.5 Pro ← Prompt + Context ← Similarity Search ← Question
```

1. **Upload** one or more PDF files via the left panel
2. **Build Index** — extracts text, splits into chunks, embeds with Google's `embedding-001` model, and stores vectors locally in a FAISS index
3. **Ask questions** — your question is embedded, matched against the index, and the top relevant chunks are sent to Gemini 1.5 Pro to generate a detailed answer

---

## Project Structure

```
multi-pdf-document-extractor/
│
├── frontend.py          # Streamlit UI (two-panel layout)
├── backend.py           # Core logic: PDF reading, chunking, embedding, QA chain
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not committed to git)
├── faiss_index/         # Auto-generated vector store (created after first index build)
│   ├── index.faiss
│   └── index.pkl
└── README.md
```

---

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/multi-pdf-docmind.git
cd multi-pdf-docmind
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# macOS / Linux
python -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Google API key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey). The free tier is sufficient for most use cases.

### 5. Run the app

```bash
streamlit run frontend.py
```

The app will open at `http://localhost:8501`.

---

## Usage

| Step | Action |
|------|--------|
| 1 | Upload one or more PDF files using the **left panel** |
| 2 | Click **⚡ Build Index** to process and embed the documents |
| 3 | Wait for the status badge to show **Index Ready · N chunks** |
| 4 | Type a question in the **right panel** and click **Ask →** |
| 5 | Repeat — the index persists until you upload new documents |

### Tips

- You can upload multiple PDFs at once before clicking Build Index
- The FAISS index is saved locally — if you restart the app without reuploading, the index is still there
- Click **🗑 Clear Chat** to reset the conversation history without rebuilding the index
- If a question falls outside the document content, the model will say so rather than hallucinate

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | LLM orchestration core |
| `langchain-google-genai` | Gemini LLM + embedding model integration |
| `langchain-community` | FAISS vector store integration |
| `langchain-text-splitters` | Recursive character text splitter |
| `google-generativeai` | Google Generative AI SDK |
| `PyPDF2` | PDF text extraction |
| `faiss-cpu` | Local vector similarity search |
| `python-dotenv` | Loads `.env` API keys |

---

## Configuration

You can tune the following parameters in `backend.py`:

```python
# backend.py

# Chunk size & overlap (affects retrieval granularity)
RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)

# Number of similar chunks retrieved per question
db.similarity_search(question)          # default k=4; use k=N to change

# Model temperature (0 = deterministic, 1 = creative)
ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
```

---

## Known Limitations

- **Scanned PDFs** (image-only) are not supported — PyPDF2 only extracts text layers. Use OCR tools like Adobe Acrobat or `ocrmypdf` to pre-process scanned files.
- **Very large PDFs** may take longer to index. Chunk size can be reduced for faster processing at the cost of retrieval quality.
- The FAISS index is stored locally. If you switch machines, you'll need to rebuild it.

---


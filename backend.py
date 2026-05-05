# ------------ Importing all dependencies ------------
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets["GOOGLE_API_KEY"]


# ----------- Reading multiple pdf documents ---------
def read_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:           # Guard against None on scanned/image-only pages
                text += page_text
    return text


# -------------- Splitting the text into chunks ---------------
def get_chunks_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks


# ------------- Embed chunks and persist to FAISS ----------
def get_vector_store(text_chunks):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings_model)
    vector_store.save_local("faiss_index")


# -------------- Processing uploaded PDFs (full pipeline) -----------
def process_pdfs(pdf_docs):
    """
    End-to-end pipeline: read PDFs → chunk text → embed & store in FAISS.
    Call this after the user uploads files.
    """
    raw_text = read_pdf(pdf_docs)
    if not raw_text.strip():
        raise ValueError("No extractable text found in the uploaded PDFs.")
    text_chunks = get_chunks_text(raw_text)
    get_vector_store(text_chunks)
    return len(text_chunks)


# -------------- Handling questions by users -----------
def user_input(question):
    # Step 1: Embed question and retrieve relevant chunks from FAISS
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.load_local(
        "faiss_index",
        embeddings_model,
        allow_dangerous_deserialization=True    
    )
    result_docs = db.similarity_search(question)

    # Step 2: Combine retrieved doc content into a single context string
    context = "\n\n".join(doc.page_content for doc in result_docs)

    # Step 3: Build prompt + LLM + parser using LCEL 
    prompt_template = PromptTemplate(
        template="""
Answer the question as detailed as possible from the provided context.
Make sure to provide all the details. If the answer is not in the provided
context, say "Answer is not available in the context." Do not provide a wrong answer.

Context:
{context}

Question:
{question}

Answer:
""",
        input_variables=["context", "question"],
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",     # gemini-pro is deprecated; use gemini-1.5-pro
        temperature=0.3,
    )

    # LCEL chain
    chain = prompt_template | model | StrOutputParser()

    response = chain.invoke({"context": context, "question": question})
    return response
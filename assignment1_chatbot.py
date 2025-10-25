# ...existing code...
import os
import io
import logging
import hashlib

import streamlit as st
from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Optional PDF helpers
try:
    import pdfplumber
except Exception:
    pdfplumber = None

logging.basicConfig(level=logging.INFO)

# Config
st.set_page_config(page_title="Will Olson's Assignment 1 RAG Chatbot", layout="centered")

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    st.warning("API_KEY not set in environment. Set API_KEY before running.")

client = OpenAI(api_key=API_KEY)

# Utilities
def documents_hash(docs: list[Document]) -> str:
    hasher = hashlib.sha256()
    for d in docs:
        src = ""
        try:
            src = d.metadata.get("source", "") if isinstance(d.metadata, dict) else ""
        except Exception:
            src = ""
        snippet = (d.page_content or "")[:1000]
        hasher.update(src.encode("utf-8", errors="ignore"))
        hasher.update(snippet.encode("utf-8", errors="ignore"))
    return hasher.hexdigest()

@st.cache_resource
def build_vectorstore(docs_key: str, docs: list[Document]):
    """Build and cache a Chroma vectorstore for the current `docs` list."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
    chunks = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings(model="openai.text-embedding-3-large"))
    return vectorstore

def extract_text_from_pdf_bytes(b: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber if available, fallback to naive decode."""
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(b)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n\n".join(pages)
        except Exception as e:
            logging.warning(f"pdfplumber failed: {e}")
    # fallback: try naive decode (may fail for binary PDFs)
    try:
        return b.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def docs_from_uploaded(uploaded_files):
    docs = []
    for uploaded in uploaded_files:
        name = uploaded.name
        content = None
        if name.lower().endswith((".txt", ".md")):
            content = uploaded.read().decode("utf-8", errors="ignore")
        elif name.lower().endswith(".pdf"):
            raw = uploaded.read()
            content = extract_text_from_pdf_bytes(raw)
        else:
            # Unknown type: attempt decode
            try:
                content = uploaded.read().decode("utf-8", errors="ignore")
            except Exception:
                content = ""
        docs.append(Document(page_content=content or "", metadata={"source": name}))
    return docs

# Initialize session state
if "documents" not in st.session_state:
    st.session_state["documents"] = []
if "vectorstore" not in st.session_state:
    st.session_state["vectorstore"] = None
if "docs_key" not in st.session_state:
    st.session_state["docs_key"] = None
if "messages" not in st.session_state:
    system_prompt = (
        "You are a helpful assistant for question-answering. Use any provided retrieved context when available "
        "and answer concisely (<= 3 sentences). If the answer isn't in the context, say you don't know."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

# UI: upload + chat
st.title("RAG Chatbot")
st.markdown("Upload .txt, .md, or .pdf files to be able to explore the content!")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "md", "pdf"], accept_multiple_files=True)
retriever = None
if uploaded_files:
    st.info(f"Processing {len(uploaded_files)} uploaded file(s)...")
    uploaded_docs = docs_from_uploaded(uploaded_files)
    st.session_state["documents"] = uploaded_docs
    docs_key = documents_hash(uploaded_docs)
    st.session_state["docs_key"] = docs_key
    vectorstore = build_vectorstore(docs_key, uploaded_docs)
    st.session_state["vectorstore"] = vectorstore
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
else:
    vectorstore = st.session_state.get("vectorstore")
    if vectorstore is not None:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


# ...existing code...
# Chat input: use form with an on_click callback that clears the input inside the callback
def on_submit():
    user_question = st.session_state.get("q", "").strip()
    if not user_question:
        return

    # Append user's message
    st.session_state["messages"].append({"role": "user", "content": user_question})

    # Retrieval (if available)
    docs = []
    if retriever:
        try:
            if hasattr(retriever, "similarity_search"):
                docs = retriever.similarity_search(user_question, k=5)
            elif hasattr(retriever, "get_relevant_documents"):
                docs = retriever.get_relevant_documents(user_question)
            elif hasattr(retriever, "retrieve"):
                docs = retriever.retrieve(user_question)
        except Exception as e:
            logging.error(f"Retriever error: {e}")
            docs = []

    # Prepare context and system instruction
    def format_docs(docs_list):
        return "\n\n---\n\n".join((d.page_content or "")[:2000] for d in docs_list)

    context = format_docs(docs) if docs else ""
    if context:
        system_instructions = (
            "You are a helpful assistant for question answering. Use ONLY the provided context to answer concisely (<=3 sentences). "
            "If the answer isn't in the context, say you don't know.\n\n"
            f"Context:\n{context}"
        )
    else:
        system_instructions = (
            "You are a helpful assistant for question-answering. Answer concisely (<= 3 sentences). "
            "If the answer isn't contained in the provided conversation, say you don't know."
        )

    # Build message history for the LLM
    history_messages = [m for m in st.session_state["messages"] if m["role"] != "system"]
    messages_for_llm = [{"role": "system", "content": system_instructions}] + history_messages

    # Call the LLM once and append the assistant reply
    try:
        response = client.chat.completions.create(model="openai.gpt-4o", messages=messages_for_llm)
        assistant_text = ""
        if hasattr(response, "choices") and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                assistant_text = choice.message.content
            else:
                assistant_text = choice.get("message", {}).get("content", "") or choice.get("text", "")
        else:
            assistant_text = str(response)
    except Exception as e:
        assistant_text = f"Error calling API: {e}"
        logging.error(assistant_text)

    st.session_state["messages"].append({"role": "assistant", "content": assistant_text})

    # Clear the form input safely (we are inside the callback)
    st.session_state["q"] = ""

with st.form("ask_form"):
    st.text_input("Ask your questions about the source text:", key="q", placeholder="Type your question here...")
    st.form_submit_button("Send", on_click=on_submit)
# ...existing code...

# Display chat history using Streamlit chat UI
for msg in st.session_state["messages"]:
    if msg["role"] == "system":
        continue
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
    # ...existing code...
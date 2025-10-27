import os
import os
import io
import logging
import hashlib
from pathlib import Path

import streamlit as st
from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)

# Config
st.set_page_config(page_title="RAG Chatbot", layout="centered")

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    st.warning("API_KEY not set in environment. Set API_KEY before running.")

client = OpenAI(api_key=API_KEY)
llm = ChatOpenAI(model="openai.gpt-4o", temperature=0.2)




def documents_hash(docs: list[Document]) -> str:
    hasher = hashlib.sha256()
    for d in docs:
        src = ""
        try:
            if isinstance(d.metadata, dict):
                src = d.metadata.get("source", "")
        except Exception:
            src = ""
        snippet = (d.page_content or "")[:1000]
        hasher.update(src.encode("utf-8", errors="ignore"))
        hasher.update(snippet.encode("utf-8", errors="ignore"))
    return hasher.hexdigest()


@st.cache_resource
def build_vectorstore(docs_key: str):
    """Build and cache a Chroma vectorstore for the current `documents` list.
    The function is keyed by `docs_key` to avoid pickling the vectorstore itself.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings(model="openai.text-embedding-3-large"))
    return vectorstore


def extract_text_from_pdf_bytes(b: bytes) -> str:
    """Try to extract text from PDF bytes using pdfplumber, fallback to pypdf."""
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(b)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n\n".join(pages)
    except Exception as e:
        logging.info(f"pdfplumber failed: {e}; falling back to pypdf")
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(b))
            texts = []
            for p in reader.pages:
                try:
                    texts.append(p.extract_text() or "")
                except Exception:
                    texts.append("")
            return "\n\n".join(texts)
        except Exception as e2:
            logging.error(f"Failed to extract PDF: {e2}")
            return ""


def docs_from_uploaded(uploaded_files):
    docs = []
    for uploaded in uploaded_files:
        fname = uploaded.name
        content_bytes = uploaded.read()
        if fname.lower().endswith((".txt", ".md")):
            text = content_bytes.decode("utf-8", errors="replace")
        elif fname.lower().endswith(".pdf"):
            text = extract_text_from_pdf_bytes(content_bytes)
        else:
            text = content_bytes.decode("utf-8", errors="replace")
        docs.append(Document(page_content=text, metadata={"source": fname}))
    return docs


# We only use user-uploaded documents as context. Start with empty documents list.
documents = []
knowledge_base = ""


# UI: upload + chat
st.title("RAG Chatbot")
st.markdown("Upload .txt, .md, or .pdf files to add to the knowledge base used for retrieval.")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "md", "pdf"], accept_multiple_files=True)
retriever = None
if uploaded_files:
    st.info(f"Processing {len(uploaded_files)} uploaded file(s)...")
    uploaded_docs = docs_from_uploaded(uploaded_files)
    # Use ONLY uploaded docs as the source of truth
    documents = uploaded_docs
    # rebuild vectorstore and retriever (keyed by document hash)
    docs_key = documents_hash(documents)
    vectorstore = build_vectorstore(docs_key)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


user_question = st.text_input("Ask a question about the source text:")

if "messages" not in st.session_state:
    system_prompt = knowledge_base + "\n\nYou are a helpful assistant. Use the knowledge base above when responding."
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

if user_question:
    st.session_state["messages"].append({"role": "user", "content": user_question})
    if retriever:
        # VectorStore retriever APIs differ between versions. Try several common methods.
        try:
            if hasattr(retriever, "similarity_search"):
                docs = retriever.similarity_search(user_question, k=5)
            elif hasattr(retriever, "get_relevant_documents"):
                # LangChain Retriever API
                docs = retriever.get_relevant_documents(user_question)
            elif hasattr(retriever, "retrieve"):
                docs = retriever.retrieve(user_question)
            else:
                raise AttributeError("Retriever has no supported retrieval method")
        except Exception as e:
            logging.error(f"Retriever error: {e}")
            docs = []
        context = "\n\n---\n\n".join(d.page_content for d in docs)
        system_instructions = (
            "You are a helpful assistant for question answering. Use ONLY the provided context to answer concisely (<=3 sentences).\n"
            "If the answer isn't in the context, say you don't know.\n\n"
            f"Context:\n{context}"
        )
        messages = [{"role": "system", "content": system_instructions}, {"role": "user", "content": user_question}]
    else:
        messages = st.session_state["messages"]

    # Call the OpenAI client
    with st.spinner("Generating response..."):
        try:
            response = client.chat.completions.create(model="openai.gpt-4o", messages=messages)
            assistant_text = response.choices[0].message.content
        except Exception as e:
            assistant_text = f"Error calling API: {e}"
            logging.error(assistant_text)

    st.session_state["messages"].append({"role": "assistant", "content": assistant_text})


# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "system":
        continue
    if msg["role"] == "user":
        st.write(f"You: {msg['content']}")
    else:
        st.write(f"Assistant: {msg['content']}")


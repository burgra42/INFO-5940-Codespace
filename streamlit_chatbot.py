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
st.set_page_config(page_title="Will Olson's INFO 5940 RAG Chatbot", layout="centered")

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
def build_vectorstore(docs_key: str, docs: list):
    """Build and cache a Chroma vectorstore for the current `docs` list.
    Keyed by docs_key so Streamlit won't try to pickle the vectorstore itself.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    chunks = text_splitter.split_documents(docs)
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
if "messages" not in st.session_state:
    # No knowledge_base variable anymore — use a concise default system prompt.
    system_prompt = (
        "You are a helpful assistant for question-answering. Use any provided retrieved context when available "
        "and answer concisely (<= 3 sentences). Answer conversationally with the user. You are interested in thier curiousity. If the answer isn't in the context, let the user know that the answer does not appear to be in the supplied documents."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]


# UI: upload + chat
st.title("Will's Document RAG Chatbot")
st.markdown("Upload .txt, .md, or .pdf files to add to discuss with the almighty bot!")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "md", "pdf"], accept_multiple_files=True)
retriever = None
if uploaded_files:
    st.info(f"Processing {len(uploaded_files)} uploaded file(s)...")
    uploaded_docs = docs_from_uploaded(uploaded_files)
    # persist uploaded docs in session_state
    st.session_state["documents"] = uploaded_docs
    docs_key = documents_hash(uploaded_docs)
    st.session_state["docs_key"] = docs_key
    # build (or reuse cached) vectorstore keyed by docs_key
    vectorstore = build_vectorstore(docs_key, uploaded_docs)
    st.session_state["vectorstore"] = vectorstore
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
else:
    # reuse any previously-built vectorstore from session_state
    vectorstore = st.session_state.get("vectorstore")
    if vectorstore is not None:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


# Handle user input and produce exactly one assistant response per submission.
# (Removes the duplicated API call / duplicated append and the stray knowledge_base block.)
# Replace the single st.text_input + immediate handling with a form + on_click callback
def on_submit():
    user_question = st.session_state.get("q", "").strip()
    if not user_question:
        return

    # persist the user's query in the conversation history
    st.session_state["messages"].append({"role": "user", "content": user_question})

    # retrieve relevant docs if a retriever exists
    docs = []
    if retriever:
        try:
            if hasattr(retriever, "similarity_search"):
                docs = retriever.similarity_search(user_question, k=5)
            elif hasattr(retriever, "get_relevant_documents"):
                docs = retriever.get_relevant_documents(user_question)
            elif hasattr(retriever, "retrieve"):
                docs = retriever.retrieve(user_question)
            else:
                docs = []
        except Exception as e:
            logging.error(f"Retriever error: {e}")
            docs = []

    # build the system prompt (include context when available)
    context = "\n\n---\n\n".join(d.page_content for d in docs) if docs else ""
    if context:
        system_instructions = (
            "You are a helpful assistant for question-answering. Use any provided retrieved context when available "
            "and answer concisely (<= 3 sentences). Answer conversationally with the user. You are interested in their curiosity. If the answer isn't in the context, let the user know that the answer does not appear to be in the supplied documents.\n\n"
            f"Context:\n{context}"
        )
    else:
        system_instructions = (
            "You are a helpful assistant for question-answering. Use any provided retrieved context when available "
            "and answer concisely (<= 3 sentences). Answer conversationally with the user. You are interested in their curiosity. If the answer isn't in the context, let the user know that the answer does not appear to be in the supplied documents."
        )

    # prepare messages to send (system + history). user's latest message already appended above.
    history_messages = [m for m in st.session_state["messages"] if m["role"] != "system"]
    messages_for_llm = [{"role": "system", "content": system_instructions}] + history_messages

    # single API call, robust extraction of text, append once
    with st.spinner("Generating response..."):
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

    # Clear the form input safely (we're inside the callback)
    st.session_state["q"] = ""


# render single form (input clears on submit via on_submit)
with st.form("ask_form"):
    st.text_input("Ask your questions about the uploaded documents here:", key="q", placeholder="You can keep the converstaion going here...")
    st.form_submit_button("Send", on_click=on_submit)



# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "system":
        continue
    if msg["role"] == "user":
        st.write(f"You: {msg['content']}")
    else:
        st.write(f"Assistant: {msg['content']}")


import streamlit as st
import os
from openai import OpenAI
from os import environ
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_schema import Document


client = OpenAI(
	api_key=os.environ["API_KEY"],
	base_url="https://api.ai.it.cornell.edu",
)

st.title("📝 File Q&A with OpenAI")
uploaded_file = st.file_uploader("Upload an article", type=("txt", "md"))

question = st.chat_input(
    "Ask something about the article",
    disabled=not uploaded_file,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask something about the article"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question and uploaded_file:
    # Read the content of the uploaded file
    file_content = uploaded_file.read().decode("utf-8")
    print(file_content)

    # Split the text into chunks for RAG
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,  # Set chunk size to divide the text
        chunk_overlap=0  # Set overlap size between chunks (optional)
    )

    chunks = text_splitter.split_documents(documents)

    # Store the chunks in a vector store
    vectorstore = Chroma.from_documents(
            documents=chunks, 
            embedding=OpenAIEmbeddings(model="openai.text-embedding-3-large")
            )
    
    # Append the user's question to the messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

   # Retreive relevant chunks from the vector store
   retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
   def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
   
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai.gpt-4o",  # Change this to a valid model name
            messages=[
                {"role": "system", "content": f"Here's the content of the file:\n\n{file_content}"},
                *st.session_state.messages
            ],
            stream=True
        )
        response = st.write_stream(stream)

    # Append the assistant's response to the messages
    st.session_state.messages.append({"role": "assistant", "content": response})
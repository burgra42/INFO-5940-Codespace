import streamlit as st
from openai import OpenAI

client = OpenAI()

st.set_page_config(page_title="Hello! It's the Will Olson Show!", layout="centered")

st.title("👋 Hello from Will!")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you today?"}]
        
for msg in st.session_state.messages:
    if msg['role'] != 'system':
        st.chat_message(msg['role']).write(msg['content'])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai.gpt-4o",
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

st.caption("This is a test app for INFO 5940 Fall 2025.")
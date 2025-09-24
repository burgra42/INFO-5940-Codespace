import streamlit as st
from openai import OpenAI

client = OpenAI()

st.set_page_config(page_title="Hello! It's the Will Olson Show!", layout="centered")

st.title("👋 Hello from Will!")

import pathlib

if "messages" not in st.session_state:
    prompt_path = pathlib.Path("/workspaces/INFO-5940-Codespace/data/hotel_guest_system_prompt.txt")
    if prompt_path.exists():
        with open(prompt_path, "r") as f:
            system_prompt = f.read().strip()
    else:
        system_prompt = "You are acting as a helpful training coach to assist hotel school student employees at a hotel. Your mission is to, upon first user interaction, identify yourself as such and ask if the student is ready to begin. When they say yes, your response should begin a back and forth dialogue where you ask them questions about their training and they respond. You should then provide feedback on their responses and guide them through the training process. Make up an issue that a hotel guest would come to the front desk to report. The goal is for the student to satisfy the guest."
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hello! I am your training coach for hotel school student employees. Are you ready to begin your training?"}
    ]
        
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
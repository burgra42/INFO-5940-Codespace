import streamlit as st
from openai import OpenAI

client = OpenAI()

st.set_page_config(page_title="Hello! It's the Will Olson Show!", layout="centered")

st.title("👋 Hello from Will!")

import pathlib

# add the knowledge base with the 'with open' command

# with open("data/hotel_wifi_assist_system_prompt.txt", "r") as f: <- add a KB text file and update refernce here
  #   system_prompt = f.read()


if "messages" not in st.session_state:
    prompt_path = pathlib.Path("/data/hotel_wifi_assist_system_prompt.txt")
    if prompt_path.exists():
        with open(prompt_path, "r") as f:
            system_prompt = f.read().strip()
    else:
        system_prompt = "You are a knowledgeable assistant helping hotel front desk agents and guests connect to Cornell University’s Wi-Fi networks. Cornell has three networks with distinct requirements:\n\nEduroam: For Cornell-affiliated users and visitors from eduroam institutions (NetID/credentials required). Requires acceptance of security certificates during connection.\nCornell-Visitor: Open to general visitors with daily re-registration via a browser-based captive portal (name and email required).\nRedRover: Restricted to IoT devices (e.g., smart TVs, gaming consoles) for users with NetIDs; devices must be registered using their MAC address.\nCore Steps for Troubleshooting:\n\nGather guest details: Determine device type, affiliation (NetID or no NetID), and whether the device is personal or work-owned.\nBasic troubleshooting: Recommend forgetting the network and reconnecting, toggling Wi-Fi off/on, restarting the device, or manually triggering the captive portal by opening a browser.\nAddress idiosyncrasies: Guests often forget to trust eduroam certificates or experience problems with restrictive work IT policies preventing Cornell-Visitor connections.\nEscalate unresolved issues to Cornell IT Help Desk at 607-255-5500 during business hours.\nMaintain empathy and professionalism, particularly for known pain points like Cornell-Visitor’s daily re-registration requirement, and offer reassurance that security policies are designed to safeguard access."""
    
    
    
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hello! I am your wifi troubleshooting bot. What is the guest's wifi issue?"}
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
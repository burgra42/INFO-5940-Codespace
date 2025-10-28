# Instructions for Running `assignment1_chatbot.py`

## Overview

`assignment1_chatbot.py` is a chatbot program powered by **Streamlit** and RAG (Retrieval-Augmented Generation). Users can upload files, and the bot will process the content to build a vectorstore for conversational retrieval. This README provides step-by-step instructions for running and interacting with the chatbot.

---

## How to Run the Program

1. **Open the Terminal**:
   - Navigate to the directory where the file `assignment1_chatbot.py` is located.

2. **Run the Program**:
   - Use the following command:
     ```bash
     streamlit run assignment1_chatbot.py
     ```

---

## How to Use the Chatbot
1. **Uploading Files**:
   - After the program launches, upload your files using one of the following methods:
     - Drag and drop the files into the upload area.
     - Click on the 'Browse Files' button to select files manually.
   - File types supported:
     - `.txt`, `.pdf`, `.md`
   - Multiple file uploads are supported in a single session.

2. **File Processing**:
   - Wait while the bot processes the uploaded files and builds the **vectorstore**. You will see a notification indicating processing progress.

3. **Start a Conversation**:
   - Use the **text input box** to begin your conversation with the chatbot.
   - You can use the same input box to continue the conversation.

4. **Add More Documents**:
   - You can upload additional files during your current session. The bot will process the new files and incorporate them into the existing vectorstore.

---

### Example Workflow
1. Run the program:  
   ```bash
   streamlit run assignment1_chatbot.py
   ```

2. Upload the files:
   - **File types supported**: `.txt`, `.pdf`, and `.md`

3. Start chatting:
   - Type in the text input box.

4. Upload new files:
   - Add more files as needed during the session.

---

## Additional Notes
- Ensure that **Streamlit** is installed in your Python environment before running the program:
  ```bash
  pip install streamlit
  ```
- The chatbot's vectorstore is session-specific, meaning it processes uploaded documents for each session separately.

---

## Troubleshooting
- If you experience issues:
  - Ensure Python and Streamlit are correctly installed.
  - Ensure the uploaded files conform to the supported formats (`.txt`, `.pdf`, `.md`).
  - Check for any error messages in the terminal for further debugging.

---

##Features
* My application features a RAG chatbot that converses with the user in a conversational tone.
* The application responds using only the information in the text and alerts the user when the awswer to thier question is not in the supplied text. 
* The application enables the user to upload more documents as they converse.

** Changes to the provided configurations
* I made a great many changes to the original file
* I did my best to document them in the ref-log.md file
* At one point, I actually everything and started over
* After that, I left the original 'chat_with_pdf.py' file unchnaged so I could refer to it in its original form.
    * I iterated through the 'streamlit_chatbot.py' file before finally writing the 'assignment1_chatbot.py' file.
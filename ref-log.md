## Generative AI Use
    * I used GROK to help write the initial code. 
    * I ran this command to install some additonal resources based on GROk's reposnse
        * pip install streamlit openai langchain sentence-transformers faiss-cpu
    * I used this becasue I am new to coding and we discussed GROK 4's proficiency in code writing during class so I wanted to see how it worked. 
    * I installed pdfplumber using this command to enable the chat to accept PDF files
        * pip install pdfplumber


## Hard Reset
    * I have run into a lot of version discrepencies and plan to roll back all of this work to the previous commit using the git reset --hard HEAD command

## More Generative AI use  
    * I am now using gpt-4o to assist me in inserting the RAG text splitting and vectorizing code in the correct place
    * I created a new Jupyter notebook to mock up the RAG 
    * I used Github's Copilot AI to help with the code
    * I installed pdfplumber and pypdf to benable processing of PDF files
    * I have the bot working but the converstaional piece is missing. I think I need to add code to tell it to continue the session with the RAG data and the user comments. 
    * I used Github Copilot extensively to trouobleshoot the code
    * I have the chatbot reading PDFs, but it is not yet converstaional and the RAG remembers the previous PDF when refreshing. This may be fixed by closing the browser tab and opening a new one or starting a new session. 
    * I used so much Copilot help that I asked it to summarize the help it provided.
        Environment / packages
	•	Environment / packages
	◦	Recommended pip installs provided (langchain, langchain-openai, chromadb, openai, streamlit, tiktoken, pdfplumber, etc.) and advice to restart the app/kernel after installs.
	•	Import & package fixes
	◦	Swapped invalid imports (e.g., langchain_schema) for correct LangChain imports:
	▪	langchain.text_splitter.RecursiveCharacterTextSplitter
	▪	langchain_openai.OpenAIEmbeddings
	▪	langchain.vectorstores.Chroma
	▪	langchain.schema.Document
	◦	Addressed LangChain deprecation warning by suggesting langchain-openai.
	•	RAG pipeline implemented
	◦	Added helpers:
	▪	documents_hash(docs): SHA256 key for docs caching
	▪	build_vectorstore(docs_key, docs): @st.cache_resource Chroma vectorstore builder using text splitting + embeddings
	▪	docs_from_uploaded(uploaded_files): load .txt/.md/.pdf into langchain Document objects
	▪	extract_text_from_pdf_bytes(b): pdfplumber fallback + naive decode
	◦	Use retriever = vectorstore.as_retriever(...), and format_docs to form context.
	•	Streamlit session management & conversation persistence
	◦	Persist documents, vectorstore, docs_key, and messages in st.session_state to maintain multi-turn conversation across reruns.
	◦	Use st.session_state["messages"] to store the full chat history (system, user, assistant).
	•	Removed broken/unused knowledge_base variable
	◦	Replaced with a concise default system prompt and/or inclusion of retrieved context on each turn.
	•	Single-response guarantee & duplicate-response fixes
	◦	Ensured only a single LLM API call per user submission.
	◦	Removed API calls from the display/render loop to prevent repeated appends and runaway responses.
	◦	Appended assistant reply exactly once after the API call.
	•	Streamlit widget-backed session_state errors and fix
	◦	Explained "widget-backed session state key" and why assigning to a widget key after widget creation raises an error.
	◦	Solved by using st.form with a submit callback (on_click) so clearing the input (st.session_state["q"] = "") happens safely inside the callback.
	•	Form UX & behavior
	◦	Provided options and working implementation:
	▪	Use st.form + st.form_submit_button with on_click callback to process, append messages, call retriever/LLM, and clear input.
	▪	Alternative approaches: initialize key before widget; use on_change callback.
	◦	CSS pin-to-bottom example and button alignment were provided; image-in-button advised against, used "Send" label instead.
	•	Debugging suggestions
	◦	If duplication persists, print the raw LLM response object to adapt the response extraction logic.
	◦	Restart Streamlit and kernel after package or code changes.
	•	Files and edits
	◦	Main edits suggested for: chat_with_pdf.py, streamlit_chatbot.py, assignment1_chatbot.py (provided complete replacement/code blocks for the form, callbacks, vectorstore building, and helper functions).

	### Assistance added (2025-10-26)
- Fixed incorrect imports and recommended installing langchain-openai, chromadb, openai, streamlit, tiktoken, pdfplumber, pypdf.
- Implemented RAG helpers: documents_hash (SHA256), build_vectorstore (cached Chroma), docs_from_uploaded, extract_text_from_pdf_bytes (pdfplumber / pypdf fallback).
- Addressed LangChain deprecation warnings and suggested updated import paths.
- Persisted documents, vectorstore, docs_key, and chat history in `st.session_state` for multi-turn conversations.
- Ensured a single LLM API call per user submission; removed duplicate calls in render loop to prevent repeated assistant responses.
- Explained "widget-backed session state key" issue and implemented a safe `st.form` + `on_click` callback to clear the input inside the callback.
- Provided robust retriever usage (handles `similarity_search`, `get_relevant_documents`, `retrieve`) and context formatting for system prompt.
- Added CSS suggestion to pin the form to the bottom (exercise caution; DOM-dependent) and recommended using a text label ("Send") instead of an image for the submit button.
- Debugging guidance: print raw LLM response when duplicate text persists; restart Streamlit/kernel after package changes.
- Located and removed stray `st.text_input` that caused a second input box; provided line-numbered guidance and single-file replacement snippets to consolidate behavior.
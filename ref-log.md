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
    
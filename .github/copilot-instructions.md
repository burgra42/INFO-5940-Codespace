# Copilot Instructions for INFO-5940-Codespace

## Project Overview
This repository is for INFO 5940 coursework, primarily using Jupyter notebooks in a GitHub Codespace. The main workflow is interactive Python development and experimentation, with a focus on using OpenAI APIs and environment variables for secure access.

## Key Files and Structure
- `test.ipynb`: Main notebook for running and testing code. Demonstrates OpenAI API usage and environment variable loading.
- `requirements.txt`: Lists Python dependencies (e.g., `openai`, `python-dotenv`).
- `data/`: Contains input files such as `combined_transcript.txt` and `prompt.txt`.
- `.env` (not committed): Should contain API keys and secrets for local development.

## Developer Workflows
- **Environment Setup:**
  - Use Python 3.11.13 kernel in Codespaces.
  - Install dependencies with `pip install -r requirements.txt` if needed.
  - Load environment variables using `python-dotenv` (`load_dotenv()`).
- **Running Code:**
  - Open `test.ipynb` and run cells interactively.
  - The OpenAI API is accessed via the `openai` Python package, using the `OpenAI()` client.
- **Data Files:**
  - Place any input data in the `data/` directory. Reference these files with relative paths in code.

## Patterns and Conventions
- **API Usage:**
  - Always load environment variables before initializing the OpenAI client.
  - Use the `openai.chat.completions.create` method for chat-based completions.
  - Example:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    openai = OpenAI()
    response = openai.chat.completions.create(
        model='openai.gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello?'}
        ]
    ).choices[0].message.content
    print(response)
    ```
- **Secrets Management:**
  - Never commit `.env` files or secrets. Use `python-dotenv` to load them locally.
- **Notebook Usage:**
  - Keep code modular and use Markdown cells for explanations.
  - Test code in `test.ipynb` before moving to other files.

## Integration Points
- **OpenAI API:** Requires valid API key in environment variables.
- **Data Files:** All data should be placed in the `data/` directory for consistency.

## Additional Notes
- Follow the structure and workflow described in the `README.md`.
- If adding new dependencies, update `requirements.txt`.
- For new notebooks, follow the pattern in `test.ipynb` for environment and API setup.

---
For questions, refer to the `README.md` or ask the course instructor.

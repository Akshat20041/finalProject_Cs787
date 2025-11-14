# 🧪 Pytest Test Generator with AI Feedback Loop

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/🦜🔗-LangGraph-blueviolet)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/🎈-Streamlit-orange)](https://streamlit.io)
[![Pytest](https://img.shields.io/badge/✅-Pytest-green)](https://pytest.org)

An advanced tool that automates the creation of unit tests for Python code. It leverages the power of Large Language Models (LLMs) and the LangGraph framework to intelligently generate tests, execute them, and iteratively fix them based on the results.

## ✨ Core Features

-   **Automated Test Generation**: Analyzes your README and Python code to generate relevant `pytest` unit tests.
-   **Framework-Aware**: Intelligently detects the web framework (Flask, FastAPI, etc.) to generate appropriate, framework-specific test patterns.
-   **AI-Powered Feedback Loop**: If tests fail, the system uses an AI "critic" to analyze the errors and instructs a "generator" to fix the tests, creating a powerful, autonomous debugging cycle.
-   **Dual Interface**: Usable as both an interactive Streamlit web application and a powerful command-line tool.
-   **Modular & Extensible**: Built with a clean, modular architecture that is easy to understand and extend.

## 🤖 How It Works: The LangGraph Workflow

The core of this project is a stateful graph built with `LangGraph`. The graph defines a cyclical workflow where agents collaborate to produce and validate unit tests.

**Workflow Diagram:**
`[Detect] -> [Generate] -> [Combine] -> [Execute] -> [Critic]`
`   ^                                                    |`
`   |-------------(if tests fail)------------------------|`

-   **1. Detect Node**:
    -   Parses the user-provided `README.md` and Python source code to identify function names and detect the project's framework (e.g., Flask).

-   **2. Generate Node**:
    -   Receives the list of functions and any feedback from the Critic.
    -   Prompts an LLM to write `pytest` tests, tailored to the detected framework.

-   **3. Combine Node**:
    -   Merges the user's Python code with the newly generated test code into a single, executable test file.
    -   For frameworks like Flask, it injects the necessary fixtures (e.g., `pytest.fixture` for the app client).

-   **4. Execute Node**:
    -   Runs `pytest` on the combined file.
    -   Captures the test results, including stdout, stderr, and a detailed JSON report.

-   **5. Critic Node**:
    -   Analyzes the test results.
    -   If all tests pass, the workflow succeeds.
    -   If tests fail, it prompts another LLM to generate specific, actionable feedback on how to fix the tests. This feedback is passed back to the **Generate Node**, and the cycle repeats.

## 📂 Project Structure

The project is organized into a modular `src` directory, separating concerns for clarity and maintainability.

```
.
├── app.py                # Entry point for the Streamlit web UI.
├── requirements.txt      # Project dependencies.
├── .gitignore            # Files and directories to be ignored by Git.
├── README.md             # This file.
└── src/
    ├── __init__.py
    ├── main.py           # Entry point for the command-line interface (CLI).
    │
    ├── graph/            # Core LangGraph implementation.
    │   ├── __init__.py
    │   ├── state.py      # Defines the 'GraphState' TypedDict, the central state object passed between nodes.
    │   ├── nodes.py      # Contains the Python functions for each node in the graph (Detect, Generate, etc.).
    │   └── builder.py    # Initializes the LLMs, defines the graph structure, adds nodes/edges, and compiles it.
    │
    └── utils/            # Helper modules and utility functions.
        ├── __init__.py
        ├── file_handler.py # Functions for reading from and writing to files.
        └── parser.py     # Functions for extracting information from code and README files.
```

## 🚀 Getting Started

### Prerequisites

-   Python 3.9+
-   An API key from [Groq](https://console.groq.com/keys)

### Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API key**:
    -   Create a file named `.env` in the project root.
    -   Add your Groq API key to it:
        ```
        GROQ_API_KEY="your-api-key-here"
        ```

## 💻 Usage

This project can be run in two ways:

### 1. Web App (Streamlit)

For an interactive experience, run the Streamlit application:

```bash
streamlit run app.py
```

This will open a new tab in your browser with the application's UI, where you can upload your files and run the workflow.

### 2. Command-Line Interface (CLI)

For scripting or terminal-based use, run the `main.py` script as a module:

```bash
python -m src.main --readme /path/to/your/README.md --code /path/to/your/functions.py
```

**CLI Arguments:**

-   `--readme`: (Required) The path to the README file.
-   `--code`: (Required) The path to the Python code file.
-   `--max-iterations`: (Optional) The maximum number of feedback loops. Defaults to 3.

## 🛠️ Technology Stack

-   **Core Logic**: Python
-   **AI Workflow**: LangGraph, LangChain
-   **Language Models**: Groq API
-   **Web Interface**: Streamlit
-   **Testing**: Pytest

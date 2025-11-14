# Pytest Test Generator with Feedback Loop (LangGraph Edition)

This project uses LangGraph to create an automated workflow for generating, running, and fixing unit tests for a Python project based on its README file.

## Project Structure

- `src/`: Contains the core application logic.
  - `main.py`: The command-line entry point for the application.
  - `graph/`: Contains the LangGraph implementation.
    - `state.py`: Defines the state object for the graph.
    - `nodes.py`: Defines the functions that act as nodes in the graph.
    - `builder.py`: Builds and compiles the graph.
  - `utils/`: Contains helper utilities.
    - `file_handler.py`: For reading and writing files.
    - `parser.py`: For parsing functions and code from files.
- `requirements.txt`: Lists the Python dependencies.
- `README.md`: This file.

## Setup

1.  **Clone the repository** (if applicable)

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API key**:
    - Create a file named `.env` in the root of the project.
    - Add your Groq API key to it like this:
      ```
      GROQ_API_KEY="your-api-key-here"
      ```
    - You can get a key from the [Groq Console](https://console.groq.com/keys).

## Usage

This project has two interfaces: a command-line interface (CLI) and a web-based interface using Streamlit.

### 1. Command-Line Interface (CLI)

Run the application from the command line, providing the path to your project's README and the Python file containing the code you want to test.

```bash
python -m src.main --readme /path/to/your/README.md --code /path/to/your/functions.py
```

**CLI Arguments:**

- `--readme`: (Required) The path to the README file.
- `--code`: (Required) The path to the Python code file.
- `--max-iterations`: (Optional) The maximum number of times the feedback loop should run. Defaults to 3.

The CLI will stream its progress to the console and save the final test file as `test_final_generated.py` (on success) or `test_final_failed.py` (on failure).

### 2. Web App (Streamlit)

To use the web-based interface, run the following command:

```bash
streamlit run app.py
```

This will open a new tab in your browser with the application's UI, where you can upload your files and run the workflow interactively.

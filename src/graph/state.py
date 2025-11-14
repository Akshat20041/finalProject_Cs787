from typing import TypedDict, List, Optional, Any

class GraphState(TypedDict):
    """
    Represents the state of our graph, adapted from the original app.py.

    Attributes:
        readme_content: The content of the README file.
        user_functions: The content of the user's Python code.
        detected_functions: A list of function names detected from the source files.
        num_functions: The count of detected functions.
        iteration_results: A list of dictionaries summarizing the results of each test run.
        test_code: The string content of the generated pytest test file.
        combined_code: The user's code and test code combined for execution.
        pytest_output: The stdout from the pytest command.
        pytest_stderr: The stderr from the pytest command.
        return_code: The exit code from the pytest process.
        report: The parsed JSON report from pytest.
        iteration: The current iteration number of the feedback loop.
        max_iterations: The maximum number of iterations allowed.
        feedback: The feedback from the critic node to guide the next generation step.
        status: The current status of the graph (e.g., 'success', 'needs_fix').
        final_message: The final summary report.
        history: A log of actions taken by each node.
        framework: The detected Python framework (e.g., 'flask', 'generic').
        previous_errors: A list of errors from previous iterations.
    """
    readme_content: str
    user_functions: str
    detected_functions: List[str]
    num_functions: int
    iteration_results: List[dict]
    test_code: str
    combined_code: str
    pytest_output: str
    pytest_stderr: str
    return_code: int
    report: dict
    iteration: int
    max_iterations: int
    feedback: str
    status: str
    final_message: str
    history: List[dict]
    framework: str
    previous_errors: List[str]
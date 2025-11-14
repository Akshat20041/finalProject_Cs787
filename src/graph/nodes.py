import os
import json
import re
import subprocess
from typing import Dict

from langchain_core.messages import HumanMessage

from .state import GraphState
from ..utils.parser import (
    extract_functions_from_readme,
    extract_functions_from_python_file,
    detect_framework,
    extract_code,
    extract_user_functions,
)
# LLMs will be imported from the builder
from .builder import llm_generator, llm_critic, llm_reporter

# --- Test Execution ---

def run_pytest_json(test_file: str, timeout_sec: int = 60):
    """Run pytest and parse JSON report."""
    # Ensure the report file from previous runs is deleted
    if os.path.exists(".report.json"):
        os.remove(".report.json")

    cmd = ["pytest", test_file, "--disable-warnings", "--maxfail=20", "--json-report", "-q"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        report = None
        if os.path.exists(".report.json"):
            with open(".report.json", "r", encoding="utf-8") as f:
                report = json.load(f)
        return (proc.returncode, report, proc.stdout, proc.stderr)
    except Exception as e:
        return (-1, None, "", str(e))

# --------------------- Agent Nodes -------------------

def function_detector_node(state: GraphState) -> GraphState:
    """Detects functions from the README and the Python code."""
    print("--- Running Function Detector Node ---")
    state['history'].append({"agent": "detector", "action": "Starting function detection."})

    functions_from_readme = extract_functions_from_readme(state["readme_content"])
    functions_from_code = extract_functions_from_python_file(state["user_functions"])
    framework = detect_framework(state["user_functions"])
    state["framework"] = framework

    if functions_from_readme:
        functions = functions_from_readme
        action = f"Detected {len(functions)} functions from README."
    elif functions_from_code:
        functions = functions_from_code
        action = f"No functions in README, but found {len(functions)} in code."
    else:
        functions = []
        action = "No functions detected in either README or code."

    state["detected_functions"] = functions
    state["num_functions"] = len(functions)
    state['history'].append({"agent": "detector", "action": action})
    print(f"Detector: {action}")
    
    return state

def test_generator_node(state: GraphState) -> GraphState:
    """Generates test code based on the detected functions and framework."""
    print(f"--- Running Test Generator Node (Iteration: {state['iteration']}) ---")
    
    feedback_text = state.get("feedback", "Generate comprehensive unit tests based on the README and provided functions.")
    
    framework = state.get("framework", "generic")
    function_list = ", ".join(state["detected_functions"])
    readme_preview = state['readme_content'][:2500]
    user_functions_preview = state['user_functions'][:2500]

    framework_instructions = ""
    if framework == 'flask':
        framework_instructions = "FLASK-SPECIFIC REQUIREMENTS:\n- Use the `client` fixture for all route tests.\n- Test routes using `client.get()` or `client.post()`.\n- ALL test functions MUST have 'client' as a parameter."
    elif framework == 'fastapi':
        framework_instructions = "FASTAPI-SPECIFIC REQUIREMENTS:\n- Use `TestClient` from `fastapi.testclient`.\n- Test endpoints using `client.get()` or `client.post()`."

    prompt = f"""
You are an expert Python test generator. Your task is to generate {state['num_functions']} unit tests.

DETECTED FUNCTIONS: {function_list}
FRAMEWORK: {framework.upper()}
{framework_instructions}

CRITICAL REQUIREMENTS:
1. Generate EXACTLY ONE test function per detected function.
2. Naming convention: `test_originalfunctionname`.
3. Each test must be independent.

FEEDBACK FROM PREVIOUS RUN: {feedback_text}

README (Preview):
{readme_preview}

USER'S CODE (Preview):
{user_functions_preview}

Generate the complete Python code for the test file. Return ONLY the code wrapped in <PYTEST_FILE> tags.
<PYTEST_FILE>
# test_generated.py
import pytest
# ... other necessary imports

# ... your test functions here ...
</PYTEST_FILE>
"""
    
    messages = [HumanMessage(content=prompt)]
    response = llm_generator.invoke(messages)
    test_code = extract_code(response.content)
    
    state["test_code"] = test_code
    action = f"Generated {state['num_functions']} test functions for {framework} framework."
    state['history'].append({"agent": "generator", "action": action})
    print(f"Generator: {action}")

    return state

def combiner_node(state: GraphState) -> GraphState:
    """Combines the user's functions and the generated tests into a single file for execution."""
    print("--- Running Combiner Node ---")

    framework = state.get("framework", "generic")
    filtered_functions = extract_user_functions(state['user_functions'], state['detected_functions'])
    
    # Clean imports from user code to avoid conflicts
    filtered_functions = re.sub(r'^import\s+.*$', '', filtered_functions, flags=re.MULTILINE)
    filtered_functions = re.sub(r'^from\s+.*import\s+.*$', '', filtered_functions, flags=re.MULTILINE)

    if framework == 'flask':
        combined = f"""
import pytest
from flask import Flask, request

app = Flask(__name__)
{filtered_functions}

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

{state['test_code']}
"""
    else: # Generic or FastAPI
        combined = f"""
{filtered_functions}

{state['test_code']}
"""
    
    state["combined_code"] = combined
    action = f"Combined code for {framework} framework."
    state['history'].append({"agent": "combiner", "action": action})
    print(f"Combiner: {action}")
    
    return state

def execution_node(state: GraphState) -> GraphState:
    """Runs pytest on the combined code file."""
    print("--- Running Execution Node ---")
    
    test_file_path = "test_combined.py"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(state["combined_code"])
    
    return_code, report, stdout, stderr = run_pytest_json(test_file_path)
    
    state["return_code"] = return_code
    state["report"] = report or {}
    state["pytest_output"] = stdout
    state["pytest_stderr"] = stderr
    
    summary = report.get("summary", {}) if report else {}
    state["iteration_results"].append({
        "iteration": state["iteration"],
        "collected": summary.get("collected", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "errors": summary.get("errors", 0)
    })
    
    action = f"Executed tests. Return code: {return_code}."
    state['history'].append({"agent": "executor", "action": action})
    print(f"Executor: {action}")

    return state

def critic_node(state: GraphState) -> GraphState:
    """Analyzes the test results and provides feedback."""
    print("--- Running Critic Node ---")

    summary = state["report"].get("summary", {})
    collected = summary.get("collected", 0)
    passed = summary.get("passed", 0)
    
    if collected > 0 and passed == collected:
        state["status"] = "success"
        state["feedback"] = "All tests passed successfully."
        action = f"SUCCESS - {passed}/{collected} tests passed."
        state['history'].append({"agent": "critic", "action": action})
        print(f"Critic: {action}")
        return state

    failed_tests = []
    if state["report"].get("tests"):
        for test in state["report"]["tests"]:
            if test.get("outcome") in ["failed", "error"]:
                failed_tests.append({"name": test.get("nodeid", ""), "error": test.get("longrepr", "")[:400]})

    prompt = f"""
Analyze the pytest results and provide SPECIFIC, ACTIONABLE feedback for the test generator.

FRAMEWORK: {state['framework'].upper()}
RESULTS: {passed}/{collected} passed.
ITERATION: {state['iteration']} of {state['max_iterations']}

FAILED TESTS:
{json.dumps(failed_tests[:3], indent=2)}

PYTEST STDERR:
{state['pytest_stderr'][:800]}

YOUR TASK: Analyze the failures and provide concise feedback to fix the tests. Focus on what the *test generator* should do differently.

RESPONSE FORMAT (JSON only):
{{
  "status": "needs_fix" | "max_iterations" | "success",
  "feedback": "Your concise, actionable feedback here. Example: 'test_get_item failed. Ensure you are using client.get(\"/items/0\") and asserting the status code is 200.'"
}}
"""
    
    messages = [HumanMessage(content=prompt)]
    response = llm_critic.invoke(messages)
    
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"status": "needs_fix", "feedback": "Critic response was not valid JSON."}

    state["status"] = result.get("status", "needs_fix")
    state["feedback"] = result.get("feedback", "No feedback provided.")
    
    action = f"Analysis: {state['status']}. Feedback: {state['feedback']}"
    state['history'].append({"agent": "critic", "action": action})
    print(f"Critic: {action}")

    if state["status"] == "needs_fix":
        state["iteration"] += 1
        
    return state

def reporter_node(state: GraphState) -> GraphState:
    """Generates the final report."""
    print("--- Running Reporter Node ---")

    summary = state.get("report", {}).get("summary", {})
    passed = summary.get("passed", 0)
    collected = summary.get("collected", 0)

    prompt = f"""
Generate a concise final report for the user based on the workflow outcome.

STATUS: {state['status']}
ITERATIONS: {state['iteration']}
FRAMEWORK: {state['framework'].upper()}
FUNCTIONS DETECTED: {state['num_functions']}
FINAL TEST RESULT: {passed}/{collected} passed.

SUMMARY:
{"All tests passed successfully!" if state['status'] == 'success' else "Could not achieve 100% pass rate within the iteration limit."}

Provide a brief, clear summary for the end-user.
"""
    
    messages = [HumanMessage(content=prompt)]
    response = llm_reporter.invoke(messages)
    
    state["final_message"] = response.content
    action = "Final report generated."
    state['history'].append({"agent": "reporter", "action": action})
    print(f"Reporter: {action}")
    
    return state

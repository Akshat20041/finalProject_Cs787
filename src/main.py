import argparse
import sys
import os

# Add the project root to the Python path to allow absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils import file_handler
from src.graph.builder import main_graph
from src.graph.state import GraphState

def main():
    """
    The main entry point for the command-line application.
    """
    parser = argparse.ArgumentParser(description="Generate and run pytest tests for Python functions based on a README file.")
    parser.add_argument("--readme", required=True, help="Path to the README.md file.")
    parser.add_argument("--code", required=True, help="Path to the Python file containing the functions to test.")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum number of feedback loops to attempt.")
    
    args = parser.parse_args()

    print("--- Starting Test Generation Workflow ---")

    # 1. Read input files
    readme_content = file_handler.read_file(args.readme)
    if readme_content is None:
        sys.exit(1) # Exit if file not found

    user_functions = file_handler.read_file(args.code)
    if user_functions is None:
        sys.exit(1) # Exit if file not found

    # 2. Initialize the graph state
    initial_state = GraphState(
        readme_content=readme_content,
        user_functions=user_functions,
        detected_functions=[],
        num_functions=0,
        test_code="",
        combined_code="",
        iteration_results=[],
        pytest_output="",
        pytest_stderr="",
        return_code=-1,
        report={},
        iteration=1,
        max_iterations=args.max_iterations,
        feedback="",
        status="",
        final_message="",
        history=[],
        framework="generic",
        previous_errors=[]
    )

    # 3. Invoke the graph and stream results
    print("\n--- Invoking LangGraph ---")
    final_state = None
    for state_update in main_graph.stream(initial_state):
        # state_update is a dictionary where the key is the node that just ran
        node_name = list(state_update.keys())[0]
        node_output = list(state_update.values())[0]
        
        print(f"\n> Node '{node_name}' finished.")
        
        # You can add more detailed logging here if needed
        if node_name == "critic":
            status = node_output.get('status')
            feedback = node_output.get('feedback')
            print(f"  - Status: {status}")
            print(f"  - Feedback: {feedback}")

        final_state = node_output

    # 4. Print the final report
    print("\n--- Workflow Complete ---")
    if final_state:
        print("\n--- Final Report ---")
        print(final_state.get("final_message", "No final message was generated."))
        
        if final_state.get("status") == "success":
            print("\n--- Generated Test Code ---")
            print(final_state.get("test_code", "No test code was generated."))
            
            # Save the final test code to a file
            file_handler.write_file("test_final_generated.py", final_state.get("test_code", ""))
        else:
            print("\n--- Failing Test Code ---")
            print(final_state.get("test_code", "No test code was generated."))
            file_handler.write_file("test_final_failed.py", final_state.get("test_code", ""))

    else:
        print("An error occurred and the workflow did not complete.")

if __name__ == "__main__":
    main()

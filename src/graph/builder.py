import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from .state import GraphState
from .nodes import (
    function_detector_node,
    test_generator_node,
    combiner_node,
    execution_node,
    critic_node,
    reporter_node,
)

from langchain_groq import ChatGroq

# ------------------------- LLM Setup -------------------------
# Load environment variables from .env file
load_dotenv()

# Ensure the API key is available
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize the LLMs from the original app
# Note: The model names below are from the original app.py.
# You may need to update them to currently available models from Groq if you encounter errors.
llm_generator = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2)
llm_critic = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.1)
llm_reporter = ChatGroq(model="qwen/qwen3-32b", temperature=0.3)


# --------------------- Routing Logic -------------------

def should_continue(state: GraphState) -> str:
    """Decides the next step after the critic node."""
    print("--- Running Conditional Edge: should_continue ---")
    
    status = state.get("status", "")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if status == "success":
        print("Edge: Success. Moving to reporter.")
        return "reporter"
    
    if iteration > max_iterations:
        state["status"] = "max_iterations"
        print(f"Edge: Max iterations ({max_iterations}) reached. Moving to reporter.")
        return "reporter"
    
    if status == "needs_fix":
        print("Edge: Needs fix. Looping back to generator.")
        return "generate"
    
    print("Edge: Defaulting to reporter.")
    return "reporter"

# --------------------- Build Graph -------------------

def build_graph():
    """Builds and compiles the LangGraph workflow."""
    
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("detect", function_detector_node)
    workflow.add_node("generate", test_generator_node)
    workflow.add_node("combine", combiner_node)
    workflow.add_node("execute", execution_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("reporter", reporter_node)
    
    # Define edges
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "generate")
    workflow.add_edge("generate", "combine")
    workflow.add_edge("combine", "execute")
    workflow.add_edge("execute", "critic")
    
    # Conditional edge from critic
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "generate": "generate",
            "reporter": "reporter"
        }
    )
    
    # Final edge to the end
    workflow.add_edge("reporter", END)
    
    # Compile the graph
    app = workflow.compile()
    print("--- Graph Compiled Successfully ---")
    return app

# Create a global instance of the compiled graph
main_graph = build_graph()

import streamlit as st
from src.graph.builder import main_graph
from src.graph.state import GraphState
from src.utils.parser import extract_functions_from_readme, extract_functions_from_python_file, detect_framework

# --------------------- Streamlit UI ----------------------

st.set_page_config(page_title="Unit Test Generator with Feedback Loop", layout="wide")
st.title("🧪 Pytest Test Generator with Feedback Loop")

st.markdown("""
Upload a README and provide your function implementations. The system will:
1. Detect functions from README and identify framework (Flask, FastAPI, Django, etc.)
2. Generate tests (one per function) with framework-specific patterns
3. Run tests against your functions
4. **Feedback loop**: Fix any failing tests automatically until all pass
""")

with st.sidebar:
    st.header("⚙️ Configuration")
    max_iterations = st.slider("Max Fix Iterations", 1, 7, 3)
    st.info("System generates one test per function with naming: test_functionname")
    st.success("✨ NEW: Automatic Flask/FastAPI/Django detection")
    st.markdown("### Process")
    st.markdown("""
    1. Upload README
    2. Provide functions
    3. Click Generate
    4. Feedback loop runs
    5. Framework-aware tests
    """)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 README File")
    uploaded_file = st.file_uploader("Upload README.md", type=["md", "txt"])
    
    readme_content = None
    if uploaded_file:
        readme_content = uploaded_file.read().decode("utf-8", errors="ignore")
        with st.expander("Preview README", expanded=False):
            st.code(readme_content[:1000] + "..." if len(readme_content) > 1000 else readme_content, language="markdown")

with col2:
    st.subheader("💻 Your Functions")
    uploaded_functions_file = st.file_uploader("Upload functions.py", type=["py"])
    
    user_functions = None
    if uploaded_functions_file:
        user_functions = uploaded_functions_file.read().decode("utf-8", errors="ignore")
        with st.expander("Preview Functions", expanded=False):
            st.code(user_functions[:1000] + "..." if len(user_functions) > 1000 else user_functions, language="python")

st.divider()

if readme_content and user_functions and st.button("🚀 Generate Tests & Run Feedback Loop", type="primary", use_container_width=True):
    
    test_functions_readme = extract_functions_from_readme(readme_content)
    test_functions_code = extract_functions_from_python_file(user_functions)
    detected_framework = detect_framework(user_functions)
    
    if not test_functions_readme and not test_functions_code:
        st.error("""
        ❌ **No functions detected!**
        
        Make sure your README includes function signatures like:
        - `function_name()` in backticks
        - `def function_name(` in code blocks
        - Headers like `### function_name(args)`
        
        OR your Python file contains actual function definitions.
        """)
        st.stop()
    
    all_detected = test_functions_readme if test_functions_readme else test_functions_code
    st.info(f"✅ Pre-check: Found {len(all_detected)} functions in {detected_framework.upper()} app: {', '.join(all_detected[:5])}{'...' if len(all_detected) > 5 else ''}")
    
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
        max_iterations=max_iterations,
        feedback="",
        status="",
        final_message="",
        history=[],
        framework="generic",
        previous_errors=[]
    )
    
    config = {"configurable": {"thread_id": "streamlit_thread"}}
    
    progress_container = st.container()
    
    with st.spinner("🔄 Running workflow with feedback loop..."):
        final_state = None
        for state in main_graph.stream(initial_state, config):
            final_state = state
            
            if list(state.keys())[0] in ["detect", "generate", "combine", "execute", "critic", "reporter"]:
                node_name = list(state.keys())[0]
                node_state = list(state.values())[0]
                
                with progress_container:
                    if node_name == "detect":
                        funcs = node_state.get('detected_functions', [])
                        fw = node_state.get('framework', 'generic')
                        st.info(f"🔍 Detected {len(funcs)} functions in {fw.upper()} app: {', '.join(funcs[:8])}{'...' if len(funcs) > 8 else ''}")
                    elif node_name == "generate":
                        iter_num = node_state.get('iteration', 1)
                        fw = node_state.get('framework', 'generic')
                        if iter_num == 1:
                            st.info(f"🤖 Iteration {iter_num}: Generating {node_state.get('num_functions', 0)} {fw}-aware tests...")
                        else:
                            st.info(f"🔧 Iteration {iter_num}: Fixing tests based on feedback...")
                    elif node_name == "combine":
                        fw = node_state.get('framework', 'generic')
                        st.info(f"🔗 Iteration {node_state.get('iteration', 1)}: Combining {fw} functions with tests...")
                    elif node_name == "execute":
                        st.info(f"⚙️ Iteration {node_state.get('iteration', 1)}: Running pytest...")
                    elif node_name == "critic":
                        status = node_state.get('status', '')
                        iter_num = node_state.get('iteration', 1)
                        summary = node_state.get('report', {}).get('summary', {})
                        passed = summary.get('passed', 0)
                        collected = summary.get('collected', 0)
                        
                        if status == "success":
                            st.success(f"✅ Iteration {iter_num}: All tests passed! ({passed}/{collected})")
                        elif status == "needs_fix":
                            st.warning(f"🔄 Iteration {iter_num}: {passed}/{collected} tests passed - Fixing...")
                        elif status == "stalled":
                            st.warning(f"⚠️ Iteration {iter_num}: No improvement detected - stopping")

    if final_state:
        final_state = list(final_state.values())[0]
        
        st.divider()
        st.subheader("📊 Workflow Results")
        
        # Display metrics and results...
        # (This part is long, but should be correct as it's from the user's provided code)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Functions Detected", final_state["num_functions"])
        col2.metric("Total Iterations", final_state["iteration"])
        
        status_emoji = "✅" if final_state["status"] == "success" else "⚠️"
        col3.metric("Final Status", f"{status_emoji} {final_state['status'].replace('_', ' ').title()}")
        
        if final_state.get("report"):
            summary = final_state["report"].get("summary", {})
            col4.metric("Tests Passed", f"{summary.get('passed', 0)}/{summary.get('collected', 0)}")
        
        framework = final_state.get('framework', 'generic')
        if framework != 'generic':
            st.info(f"🎯 Framework: **{framework.upper()}** - Tests generated with {framework}-specific patterns")
        
        with st.expander("🔍 Function → Test Mapping", expanded=True):
            for i, func in enumerate(final_state["detected_functions"], 1):
                st.write(f"{i}. `test_{func}()` ← Tests → `{func}()`")
        
        st.divider()
        st.subheader("📈 Progress Across Iterations")
        
        for result in final_state["iteration_results"]:
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"**Iteration {result['iteration']}**")
            col2.metric("Collected", result['collected'])
            
            delta_passed = None
            if result['iteration'] > 1:
                prev_passed = final_state["iteration_results"][result['iteration']-2]['passed']
                delta_passed = result['passed'] - prev_passed
            
            col3.metric("Passed", result['passed'], delta=delta_passed)
            col4.metric("Failed", result['failed'])
        
        st.divider()
        st.subheader("📝 Final Test Code")
        st.code(final_state["test_code"], language="python")
        
        st.subheader("📋 Final Report")
        st.markdown(final_state["final_message"])
        
        if final_state.get("report"):
            with st.expander("🔍 Detailed Test Results"):
                tests = final_state["report"].get("tests", [])
                for t in tests:
                    nodeid = t.get("nodeid", "")
                    outcome = t.get("outcome", "")
                    if outcome == "passed":
                        st.success(f"✅ {nodeid}")
                    elif outcome == "failed":
                        st.error(f"❌ {nodeid}")
                        if t.get("longrepr"):
                            st.code(t["longrepr"][:600], language="bash")
                    elif outcome == "error":
                        st.error(f"💥 {nodeid} (Error)")
                        if t.get("longrepr"):
                            st.code(t["longrepr"][:600], language="bash")
        
        with st.expander("📜 Execution History"):
            for entry in final_state["history"]:
                agent_emoji = {"detector": "🔍", "generator": "🤖", "combiner": "🔗", "executor": "⚙️", "critic": "🔬", "reporter": "📋"}.get(entry['agent'], "•")
                st.write(f"{agent_emoji} **Iteration {entry['iteration']}** - {entry['agent'].title()}: {entry['action']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="⬇️ Download Test File", data=final_state["test_code"], file_name="test_generated.py", mime="text/x-python", use_container_width=True)
        with col2:
            st.download_button(label="⬇️ Download Combined File", data=final_state["combined_code"], file_name="test_combined.py", mime="text/x-python", use_container_width=True)

else:
    if not readme_content:
        st.info("⬆️ Please upload a README.md file")
    if not user_functions:
        st.info("💻 Please provide your functions.py file")

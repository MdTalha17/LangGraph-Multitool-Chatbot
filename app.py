"""
Streamlit Chat Application
End-to-end chatbot powered by LangGraph with Arxiv, Wikipedia, and Tavily tools.
Run with: streamlit run app.py
"""

import re
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from graph import build_graph
from tools import TOOL_INFO

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="LangGraph Multi-Tool Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🤖 LangGraph Chatbot")
    st.divider()

    # Model selector
    st.subheader("⚙️ Model")
    model_name = st.text_input(
        "Groq Model ID",
        value="qwen/qwen3-32b",
        help="Enter any model ID supported by Groq",
        label_visibility="collapsed",
    )

    st.divider()

    # Tool status cards
    st.subheader("🛠️ Active Tools")
    for tool in TOOL_INFO:
        with st.container(border=True):
            st.markdown(f"{tool['icon']}  **{tool['name']}**  🟢")
            st.caption(tool["description"])

    st.divider()

    # Clear chat button
    if st.button("🗑️  Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.graph = None
        st.rerun()

    st.caption("Powered by LangGraph • Groq • Streamlit")


# ── Session state initialisation ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state or st.session_state.get("_model") != model_name:
    st.session_state.graph = build_graph(model_name)
    st.session_state._model = model_name


# ── Header ──────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Tool AI Assistant")
st.caption("Ask anything — I can search **Arxiv**, **Wikipedia**, and the **Web** for you.")


# ── Render chat history ────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant", avatar="🤖"):
            # Show tool-call badges if the AI decided to call tools
            if msg.tool_calls:
                cols = st.columns(len(msg.tool_calls))
                for i, tc in enumerate(msg.tool_calls):
                    cols[i].info(f"🔧 {tc['name']}")
            if msg.content:
                # Strip <think>...</think> blocks from the response
                content = re.sub(r"<think>.*?</think>", "", msg.content, flags=re.DOTALL).strip()
                if content:
                    st.markdown(content)
    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant", avatar="🔧"):
            with st.expander(f"📎 Tool Result — `{msg.name}`", expanded=False):
                st.code(msg.content[:1500], language="text")


# ── Chat input & graph invocation ──────────────────────────────────────────
if prompt := st.chat_input("Ask me anything…"):
    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Invoke the graph
    human_msg = HumanMessage(content=prompt)
    all_messages = st.session_state.messages + [human_msg]

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking…"):
            result = st.session_state.graph.invoke({"messages": all_messages})

    # Update session state with full message history from the graph
    st.session_state.messages = result["messages"]

    # Rerun to render the new messages cleanly
    st.rerun()

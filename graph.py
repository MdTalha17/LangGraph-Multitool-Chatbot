"""
Graph Module
Builds the LangGraph state graph that connects the LLM with tool nodes.
The graph routes between the LLM and tools using conditional edges.
"""

from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import get_tools


class State(TypedDict):
    """Graph state schema — maintains the message history."""
    messages: Annotated[list[AnyMessage], add_messages]


def build_graph(model_name: str = "qwen/qwen3-32b"):
    """
    Build and compile the LangGraph chatbot graph.

    Args:
        model_name: The Groq model identifier to use.

    Returns:
        A compiled LangGraph graph ready for invocation.
    """
    tools = get_tools()

    # Initialize the LLM and bind tools
    llm = ChatGroq(model=model_name)
    llm_with_tools = llm.bind_tools(tools=tools)

    # Node: call the LLM with tool bindings
    def tool_calling_llm(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # Build the state graph
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))

    # Edges
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges(
        "tool_calling_llm",
        # Routes to 'tools' if the LLM made a tool call, otherwise to END
        tools_condition,
    )
    builder.add_edge("tools", "tool_calling_llm")

    return builder.compile()

"""
Tools Module
Defines and configures the external tools used by the LangGraph chatbot:
  - Arxiv: Search academic papers
  - Wikipedia: Query Wikipedia articles
  - Tavily: Web search for current events
"""

from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults


def get_tools():
    """Initialize and return all available tools."""

    # Arxiv — academic paper search
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
    arxiv_tool = ArxivQueryRun(
        api_wrapper=arxiv_wrapper,
        description="Search and retrieve academic papers from Arxiv. Use this for research papers, scientific publications, and academic content."
    )

    # Wikipedia — encyclopedia search
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
    wiki_tool = WikipediaQueryRun(
        api_wrapper=wiki_wrapper,
        description="Search Wikipedia for general knowledge, historical facts, and encyclopedic information."
    )

    # Tavily — web search for current events
    tavily_tool = TavilySearchResults(
        description="Search the web for current events, recent news, and up-to-date information."
    )

    return [arxiv_tool, wiki_tool, tavily_tool]


# Tool metadata for UI display
TOOL_INFO = [
    {
        "name": "Arxiv",
        "icon": "📄",
        "description": "Academic paper search",
    },
    {
        "name": "Wikipedia",
        "icon": "📚",
        "description": "Encyclopedia lookup",
    },
    {
        "name": "Tavily Search",
        "icon": "🌐",
        "description": "Web search (current events)",
    },
]

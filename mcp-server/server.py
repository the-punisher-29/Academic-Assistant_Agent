import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from agents.orchestrator import run_chat, planner_agent, researcher_agent, critic_agent
from agents.tools import search_curriculum, read_calendar
from langchain_core.messages import HumanMessage

# Create an MCP server
mcp = FastMCP("StudentAcademicCopilot")

@mcp.tool()
def ask_copilot(query: str) -> str:
    """Ask the Student Academic Copilot a question (Runs the full multi-agent system)."""
    return run_chat(query)

@mcp.tool()
def run_planner(query: str) -> str:
    """Run only the Planner Agent to generate a plan."""
    state = {"messages": [HumanMessage(content=query)]}
    result = planner_agent(state)
    return "\n".join(result["plan"])

@mcp.tool()
def run_researcher(plan_steps: str) -> str:
    """Run only the Researcher Agent given a list of plan steps (newline separated)."""
    plan = plan_steps.split("\n")
    state = {"plan": plan}
    result = researcher_agent(state)
    return result["context"]

@mcp.tool()
def run_critic(query: str, context: str) -> str:
    """Run only the Critic Agent given a query and gathered context."""
    state = {
        "messages": [HumanMessage(content=query)],
        "context": context
    }
    result = critic_agent(state)
    return result["messages"][-1].content

@mcp.tool()
def get_curriculum(query: str) -> str:
    """Search for curriculum information."""
    return search_curriculum(query)

@mcp.tool()
def get_calendar(query: str = "") -> str:
    """Get academic calendar information."""
    return read_calendar(query)

if __name__ == "__main__":
    mcp.run()

# Architecture

## Agent Roles

I designed three distinct agents to handle the workload:

1.  **Planner Agent**:
    *   **Role**: I act as the strategist. I take the user's complex query and break it down into a step-by-step plan.
    *   **Tools**: `save_plan` (I save my plan to a file so we can track it).
    *   **Input**: User query.
    *   **Output**: A list of actionable steps.

2.  **Content Curator (Researcher) Agent**:
    *   **Role**: I am the doer. I execute the plan by hunting down information.
    *   **Tools**:
        *   `search_curriculum`: I dig through the text files we scraped.
        *   `read_calendar`: I check the academic calendar.
        *   `web_search`: I simulate a web search for anything else.
    *   **Input**: Specific tasks from the plan.
    *   **Output**: A collection of relevant context and documents.

3.  **Critic (Responder) Agent**:
    *   **Role**: I am the quality control. I look at what the Researcher found, compare it to the original question, and write the final answer.
    *   **Tools**: `log_critique` (I log my final thoughts to a file).
    *   **Input**: Original query, Plan, Retrieved Context.
    *   **Output**: The final answer for the student.

## Message Schema

My agents talk to each other using a shared state dictionary. It looks like this:

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    plan: List[str]
    context: str
    critique: str
```

## MCP Integration

I've built this project around the Model Context Protocol (MCP):

-   **The Server (`mcp-server/server.py`)**: This hosts my agents. I exposed tools like `run_planner`, `run_researcher`, and `run_critic` so they can be called individually, plus a main `ask_copilot` tool that runs the whole chain.
-   **The Client (`app.py`)**: The UI doesn't run the agents directly. Instead, it acts as an MCP Client. It connects to the server via stdio and sends the user's query to the `ask_copilot` tool. This proves that my architecture is modular and standards-compliant!

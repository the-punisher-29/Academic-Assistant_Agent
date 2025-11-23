# Research Note: Student Academic Copilot

## 1. Introduction
I built the Student Academic Copilot as a Multi-Agent System to help students at IIT Jodhpur navigate the chaos of academic life. I used a lightweight orchestration framework (LangGraph) and powerful Large Language Models (via Groq) to give accurate, context-aware answers.

## 2. Setup and Architecture
### 2.1 Architecture
I decided on a linear multi-agent architecture to keep things organized:
1.  **Planner**: First, I break the query into steps.
2.  **Researcher**: Then, I go out and find the data using my tools.
3.  **Critic**: Finally, I put it all together and double-check the quality.

[Figure 1: Architecture Diagram Placeholder - showing User -> Gradio -> Planner -> Researcher -> Critic -> Response]

### 2.2 Implementation Details
-   **Orchestrator**: LangGraph (it's great for state management).
-   **LLM**: I'm using `openai/gpt-oss-120b` on Groq. It's fast and handles the context well.
-   **Interface**: I built a Gradio UI that acts as an MCP Client.
-   **Integration**: The core logic is wrapped in an MCP Server. This means I can easily plug my agents into other tools later.

## 3. Methodology
I set up a shared state that holds the conversation history, the current plan, and any gathered context. This allows my agents to collaborate. The Planner ensures I don't get overwhelmed by complex questions, the Researcher focuses purely on digging up data (using the scraper I wrote), and the Critic ensures I don't hallucinate an answer.

## 4. Evaluation and Metrics
I didn't just build it; I tested it. I created a harness with 6 programmatic test cases covering curriculum, calendar, and general program queries.

### 4.1 Metrics
-   **Success Rate**: Did I find the keywords I was looking for?
-   **Latency**: How long did I take to think?
-   **Tool Usage**: Did I actually use the tools I gave myself?

[Figure 2: Latency vs Query Complexity Placeholder]

### 4.2 Key Insights
-   **Decomposition is powerful**: Breaking down the query made a huge difference for multi-part questions.
-   **Context is everything**: If the Researcher fails, the Critic fails. I had to tweak the scraper and search logic to make sure I was feeding the right data to the LLM.
-   **MCP is flexible**: Separating the Client and Server made the architecture much cleaner.

## 5. Conclusion
This project showed me that multi-agent systems are perfect for specialized domains like academic advising. By giving agents specific roles and tools, I created a system that is much more reliable than a simple chatbot.

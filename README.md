# Student Academic Copilot

## Overview
Hi! I've built this sophisticated question-answering system to help students (like me!) ask questions about the school calendar, university curriculum, course suggestions, and career paths. I designed this using a Multi-Agent System architecture to ensure the answers are well-planned and accurate.

## Demo Video
Watch the system in action here: [Demo Video](https://drive.google.com/file/d/1kW8yVngq9sqNUgjf4KGQxiPeBEMCYuDe/view?usp=sharing)

## Architecture
I've detailed the inner workings in [ARCH.md](ARCH.md), but in short: I use a Planner to break down questions, a Researcher to find the data, and a Critic to make sure the answer makes sense.

## Directory Structure
- `/agents/`: My agent code and orchestration logic (using LangGraph).
- `/mcp-server/`: My custom MCP implementation. The server runs the agents.
- `/data/`: The artifacts I scraped from IIT Jodhpur data.
- `/eval/`: My test suite and metrics.
- `app.py`: The interactive UI. It acts as an MCP Client that talks to the server!

## How to Run

### Prerequisites
- Python 3.10+
- A Groq API Key (I use `openai/gpt-oss-120b`). Set it as `GROQ_API_KEY` in a `.env` file.

### Installation
1.  First, I install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Step 1: Get the Data
I wrote a scraper to fetch the latest curriculum and calendar info. You need to run this first so the agents have something to read:
```bash
python data/scraper.py
```

### Step 2: Run Evaluations (Optional)
If you want to see how well my agents perform against the test cases I wrote:
```bash
python eval/evaluate.py
```

### Step 3: Run the Application
This is the cool part. When you run the app, it starts the MCP server in the background and connects to it as a client:
```bash
python app.py
```
Then just open the link in your browser!

### Running the MCP Server Standalone
If you want to connect a different client (like Claude Desktop) to my agents, you can run the server directly:
```bash
python mcp-server/server.py
```

## Contracts and Assumptions
- I assume you have a valid Groq API key.
- The data in `/data/` is static once scraped, so run the scraper if the website changes.
- My agents communicate via a shared state in LangGraph.

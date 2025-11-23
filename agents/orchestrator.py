import os
import operator
from typing import Annotated, List, Sequence, TypedDict, Union
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("GROQ_API_KEY") == "your_groq_api_key_here":
    print("Error: Please replace 'your_groq_api_key_here' in .env with your actual Groq API key.")

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from agents.tools import search_curriculum, read_calendar, web_search, save_plan, log_critique

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    plan: List[str]
    context: str
    critique: str

# --- LLM Setup ---
# Ensure GROQ_API_KEY is set in environment variables
if "GROQ_API_KEY" not in os.environ:
    # Fallback for demo purposes or instruct user
    print("Warning: GROQ_API_KEY not found in environment.")

# Using the user-specified model and parameters
llm = ChatGroq(
    model="openai/gpt-oss-120b", # As requested
    temperature=1,
    max_tokens=8192,
    model_kwargs={
        "top_p": 1,
        # "reasoning_effort": "medium" # Note: ChatGroq might not support this param directly yet, uncomment if supported
    },
    timeout=None,
    max_retries=2,
)

# --- Agents ---

def planner_agent(state: AgentState):
    print("--- PLANNER ---")
    messages = state["messages"]
    user_query = messages[0].content
    
    system_prompt = (
        "You are a Planner Agent. Your job is to break down the user's query into a list of actionable steps "
        "for a Researcher Agent. Output ONLY the list of steps, one per line."
    )
    
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_query)])
    plan_text = response.content
    plan = plan_text.strip().split("\n")
    
    # Tool Call: Save the plan
    save_plan(plan_text)
    
    return {"plan": plan, "messages": [AIMessage(content=f"Plan: {plan_text}")]}

def researcher_agent(state: AgentState):
    print("--- RESEARCHER ---")
    plan = state["plan"]
    context = state.get("context", "")
    
    # Simple execution: iterate through plan and decide which tool to use
    # In a more complex agent, this would be an LLM loop. 
    # Here we will ask the LLM to pick a tool for the current plan step.
    
    system_prompt = (
        "You are a Researcher Agent. You have access to the following tools:\n"
        "- search_curriculum(query): Search for curriculum info.\n"
        "- read_calendar(query): Read academic calendar.\n"
        "- web_search(query): Search the web.\n\n"
        "Given the plan, execute the necessary tools to gather information. "
        "Summarize the findings."
    )
    
    # For this simple implementation, we'll just do a keyword search based on the plan
    # using the LLM to generate tool calls (simulated here for simplicity or using bind_tools if available)
    
    # Let's just use the LLM to generate a search query for the tools
    findings = []
    for step in plan:
        # Heuristic tool selection for demo
        if "calendar" in step.lower() or "date" in step.lower():
            res = read_calendar()
            findings.append(f"Calendar Data: {res}")
        elif any(k in step.lower() for k in ["curriculum", "course", "program", "degree", "b.tech", "m.tech", "phd", "m.sc", "specialization", "department", "offer", "list"]):
            res = search_curriculum(step)
            findings.append(f"Curriculum Data for '{step}': {res}")
        else:
            res = web_search(step)
            findings.append(f"Web Search for '{step}': {res}")
            
    new_context = "\n\n".join(findings)
    return {"context": new_context, "messages": [AIMessage(content=f"Research Findings: {new_context}")]}

def critic_agent(state: AgentState):
    print("--- CRITIC ---")
    messages = state["messages"]
    user_query = messages[0].content
    context = state["context"]
    
    system_prompt = (
        "You are a Critic Agent. Review the gathered context against the user's query. "
        "If the information is sufficient, formulate a comprehensive answer. "
        "If not, point out what is missing. "
        "For this demo, assume the information is sufficient and provide the final answer."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt), 
        HumanMessage(content=f"User Query: {user_query}\n\nContext Gathered:\n{context}")
    ])
    
    # Tool Call: Log the critique/response
    log_critique(response.content)
    
    return {"messages": [response]}

# --- Graph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_agent)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("critic", critic_agent)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "critic")
workflow.add_edge("critic", END)

app_graph = workflow.compile()

def run_chat(query: str):
    inputs = {"messages": [HumanMessage(content=query)]}
    result = app_graph.invoke(inputs)
    return result["messages"][-1].content

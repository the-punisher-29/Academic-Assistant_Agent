import gradio as gr
import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Ensure API Key is set
if "GROQ_API_KEY" not in os.environ:
    print("Warning: GROQ_API_KEY environment variable not set. Please check your .env file.")

async def query_mcp_server(query: str):
    # Define server parameters to run the server script
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-server/server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Call the 'ask_copilot' tool exposed by the server
            result = await session.call_tool("ask_copilot", arguments={"query": query})
            
            # Extract text content from the result
            if result.content and hasattr(result.content[0], "text"):
                return result.content[0].text
            return str(result)

def chat_interface(message, history):
    # Gradio's default interface is synchronous, so we run the async client here
    return asyncio.run(query_mcp_server(message))

# Custom Theme for a professional, academic look
try:
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="slate",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
    ).set(
        body_background_fill="#f8fafc",
        block_background_fill="#ffffff",
        block_border_width="1px",
        block_title_text_weight="600",
        button_primary_background_fill="#4f46e5",
        button_primary_text_color="#ffffff"
    )
except Exception:
    print("Warning: Could not load custom theme. Using default.")
    theme = None

# Build the UI with Blocks
# Note: We assign theme after initialization to avoid compatibility issues with some Gradio versions
with gr.Blocks(title="IIT Jodhpur Academic Assistant") as demo:
    if theme:
        demo.theme = theme

    with gr.Row(variant="panel", elem_classes="header-row"):
        with gr.Column(scale=1, min_width=120):
            # Display the college logo
            gr.Image(
                value=os.path.join("assets", "logo.jpg"), 
                show_label=False, 
                container=False,
                height=100,
                width=100,
                elem_id="logo-img"
            )
        with gr.Column(scale=8):
            gr.Markdown(
                """
                # IIT Jodhpur Academic Assistant
                
                **Welcome.** This system is designed to assist students, faculty, and staff with inquiries regarding the **academic calendar**, **curriculum**, **course offerings**, and **program details**.
                
                Please enter your query below to retrieve information from the official institute resources.
                """
            )
    
    # The Chat Interface
    gr.ChatInterface(
        fn=chat_interface,
        examples=[
            "When does the next semester commence?",
            "Please provide details regarding the B.Tech in AI and Data Science curriculum.",
            "List the available Humanities and Social Sciences (HSS) courses.",
            "What are the requirements for the M.Tech in Cyber Physical Systems?"
        ],
        cache_examples=False,
        textbox=gr.Textbox(placeholder="Enter your academic query here...", container=False, scale=7),
    )

if __name__ == "__main__":
    # Allow access to assets folder for the logo
    demo.launch(allowed_paths=["assets"])

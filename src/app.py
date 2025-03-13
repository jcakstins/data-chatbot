import logging
import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv
from plotly.graph_objs import Figure

from bot import ChatBot
from prompt import SYSTEM_PROMPT
from tools import plot_chart, run_sqlite_query, tools_schema
from utils import generate_sqlite_table_info_query

# Compute the absolute path to the directory where this script resides (src/)
src_dir = os.path.dirname(os.path.realpath(__file__))
# Compute the project root directory (one level up from src/)
project_root = os.path.join(src_dir, "..")

# Load environment variables from the project root's .env file
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Configure logging; log file will be stored in the project root.
log_file = os.path.join(project_root, "chatbot.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler(log_file))

MAX_ITER = 5
schema_table_pairs = []

# Wrap tool functions with Chainlit steps
tool_run_sqlite_query = cl.step(type="tool", show_input="json", language="str")(run_sqlite_query)
tool_plot_chart = cl.step(type="tool", show_input="json", language="json")(plot_chart)
original_run_sqlite_query = tool_run_sqlite_query.__wrapped__

cl.instrument_openai() 
# for automatic steps

@cl.on_chat_start
async def on_chat_start():
    # Determine the user's language from the session (default to en-US if not set)
    languages = cl.user_session.get("languages")
    language = languages.split(",")[0] if languages else "en-US"

    # Use the project root as the base path for chainlit markdown files.
    root_path = Path(project_root)
    translated_chainlit_md_path = root_path / f"chainlit_{language}.md"
    default_chainlit_md_path = root_path / "chainlit.md"
    if translated_chainlit_md_path.exists():
        message_text = translated_chainlit_md_path.read_text()
    else:
        message_text = default_chainlit_md_path.read_text()

    # Send the startup message using the markdown content.
    startup_message = cl.Message(content=message_text)
    await startup_message.send()

    # Set up the chatbot with the system prompt and tool functions.
    system_message = SYSTEM_PROMPT
    tool_functions = {
        "query_db": tool_run_sqlite_query,
        "plot_chart": tool_plot_chart
    }
    cl.user_session.set("bot", ChatBot(system_message, tools_schema, tool_functions))


@cl.on_message
async def on_message(message: cl.Message):
    bot = cl.user_session.get("bot")

    msg = cl.Message(author="Assistant", content="")
    await msg.send()

    # Step 1: Process the user request and get the initial bot response.
    response_message = await bot(message.content)
    msg.content = response_message.content or ""
    if msg.content:
        await msg.update()

    # Step 2: Process tool calls iteratively (up to MAX_ITER iterations).
    cur_iter = 0
    tool_calls = response_message.tool_calls
    while cur_iter <= MAX_ITER:
        if tool_calls:
            bot.messages.append(response_message)
            response_message, function_responses = await bot.call_functions(tool_calls)

            if response_message.content:
                await cl.Message(author="Assistant", content=response_message.content).send()

            tool_calls = response_message.tool_calls

            # Display function responses (like charts) explicitly.
            function_responses_to_display = [
                res for res in function_responses if res["name"] in bot.exclude_functions
            ]
            for function_res in function_responses_to_display:
                if isinstance(function_res["content"], Figure):
                    chart = cl.Plotly(
                        name="chart", figure=function_res["content"], display="inline"
                    )
                    await cl.Message(author="Assistant", content="", elements=[chart]).send()
        else:
            break
        cur_iter += 1

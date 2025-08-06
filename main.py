import os
import requests
import chainlit as cl
from typing import cast,Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents.run import RunConfig
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel,ModelSettings
from prompts.prompts import triage_prompt,enhanced_general_prompt,enhanced_programming_prompt
from openai.types.responses import ResponseTextDeltaEvent
from data.data import load_history,save_history

load_dotenv()

# Load Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("BASE_URL")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Store conversation history
conversation_history: Dict[str, list] = load_history()

@cl.on_chat_start
async def start():

    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url=base_url,
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client,
        )

    config = RunConfig(
        model=model,
        model_provider=external_client, # type: ignore
        tracing_disabled=True
        )

    @function_tool
    async def get_weather(city: str) -> str:
        """
        Get the current weather for a given city.
        """
        try:
            result = requests.get(
                f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}"
            )
            data = result.json()

            weather_info = f"The current weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
            return weather_info

        except Exception as e:
            return f"Failed to fetch weather for {city}. Error: {str(e)}"

    # Programming Agent
    programming_agent = Agent(
        name="Programming Agent",
        instructions=enhanced_programming_prompt,
        model_settings=ModelSettings(
            temperature=0.3,
            top_p=1.0,
            max_tokens=1000,
        ),
        handoff_description="Handles programming questions.",
        model=model,
    )

    # General Agent
    general_agent = Agent(
        name="General Agent",
        instructions=enhanced_general_prompt,
        model=model,
        model_settings=ModelSettings(
            temperature=0.85,
            top_p=0.95,
            max_tokens=500,
        ),
        handoff_description="Handles general questions or those handed off from other agents.",
        tools=[get_weather],
    )

    traige_agent = Agent(
        name="Triage Agent",
        instructions=triage_prompt,
        model=model,
        handoffs=[programming_agent, general_agent],
    )

    """ Setup the chat session when a user connects.  """
    session_id = cl.user_session.get("id")
    if session_id:
        if session_id not in conversation_history:
            conversation_history[session_id] = []
    cl.user_session.set("config",config)
    cl.user_session.set("traige_agent",traige_agent)
    
    # Set the agents in user session
    cl.user_session.set("runner",Runner())

    await cl.Message(content="""
## 🤖 Welcome to Muhammad AI System

Created by Muhammad Farooq — powered by expert multi-agents.

### 🧩 Available Agents:
- 💻 **Programming Expert** – Help with code, bugs, and dev guidance.  
- 🌍 **General Expert** – For weather, life tips, and quick answers.

💬 Start chatting — we’ll route you to the right expert!
""").send()

@cl.on_message
async def main(message: cl.Message):
    """ Process incoming massages and generate response. """
    user_input = message.content

    triage_agent = cast(Agent,cl.user_session.get("traige_agent"))
    runner = cast(Runner,cl.user_session.get("runner"))
    config = cast(RunConfig,cl.user_session.get("config"))
    
    msg = cl.Message(content="Thinking...")
    await msg.send()

     # Get session ID
    session_id = cl.user_session.get("id")
    
      # Update conversation history
    if session_id is not None:
        conversation_history[session_id].append({
            "role": "user",
            "content": user_input
        })
        save_history(conversation_history)

    try:
        # Run the triage agent to determine which agent to use
        result = runner.run_streamed(triage_agent,user_input, run_config=config)

        full_response = ""

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
                token =  event.data.delta # type: ignore
                full_response += token
                msg.content = full_response
                await msg.update()

       # Update conversation history with assistant's response
        if session_id is not None:
            conversation_history[session_id].append({
            "role": "assistant",
            "content": msg.content
        })
        save_history(conversation_history)

    except Exception as e:
            msg.content = f"Error: {e}"
            await msg.update()













 # current_agent = programming_agent
        # result = await Runner.run(current_agent, input=chat_history, run_config=config)

        # if "HANDOFF_TO:general" in result.final_output:
        #     current_agent = general_agent
        #     result = await Runner.run(current_agent, input=chat_history, run_config=config)

        # elif "HANDOFF_TO:programming" in result.final_output:
        #     current_agent = programming_agent
        #     result = await Runner.run(current_agent, input=chat_history, run_config=config)    
        # if msg:
        #     msg.content = result.final_output
        #     await msg.update()
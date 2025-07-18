import os
import requests
import chainlit as cl
import asyncio
from typing import cast
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents.run import RunConfig
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, ModelProvider
from prompts.prompts import programming_prompt,general_prompt,triage_prompt

load_dotenv()

# Load Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("BASE_URL")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

 # Gemini model provider
class GeminiModelProvider(ModelProvider):
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
            )

    def get_model(self,model_name="gemini-2.0-flash"):
        return OpenAIChatCompletionsModel(
            model=self.model_name,
            openai_client=self.client
            )

model_provider = GeminiModelProvider(api_key=gemini_api_key)

    # Model config
config = RunConfig(model=model_provider.get_model(),model_provider=model_provider,tracing_disabled=True)

@cl.on_chat_start
async def start():

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
        handoff_description="Handles programming questions.",
        instructions=programming_prompt,
        model=model_provider.get_model(),
    )

    # General Agent
    general_agent = Agent(
        name="General Agent",
        handoff_description="Handles general questions or those handed off from other agents.",
        instructions=general_prompt,
        model=model_provider.get_model(),
        tools=[get_weather],
    )

    traige_agent = Agent(
        name="Triage Agent",
        instructions=triage_prompt,
        model=model_provider.get_model(),
        handoffs=[programming_agent, general_agent],
    )

    programming_agent.handoffs.append(traige_agent)
    general_agent.handoffs.append(traige_agent)

    """ Setup the chat session when a user connects.  """
    cl.user_session.set("chat_history",[])
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
    
    triage_agent = cast(Agent,cl.user_session.get("traige_agent"))
    runner = cast(Runner,cl.user_session.get("runner"))
    config = cast(RunConfig,cl.user_session.get("config"))
    chat_history = cl.user_session.get("chat_history") or []

    chat_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="Thinking...")
    await msg.send()

    try:
        # Run the triage agent to determine which agent to use
        result = runner.run_streamed(triage_agent, input=chat_history, run_config=config)

        full_response:str = ""

        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data,"delta"):
                token = cast(str, event.data.delta)
                if token:
                    full_response += token
                    msg.content = full_response
                    await msg.update()
                    await asyncio.sleep(0.10)  # Add a small delay to simulate typing

        chat_history.append({"role":"assistant","content": full_response})
        cl.user_session.set("chat_history",chat_history)

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
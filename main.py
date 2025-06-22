from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, ModelProvider, AsyncOpenAI
from agents.run import RunConfig
from dotenv import load_dotenv
import requests
import os
import chainlit as cl
from typing import cast

load_dotenv()

# Load Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("BASE_URL")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

@cl.on_chat_start
async def start():
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

        def get_model(self):
            return OpenAIChatCompletionsModel(
                model=self.model_name,
                openai_client=self.client
            )

    model_provider = GeminiModelProvider(api_key=gemini_api_key)

    # Model config
    config = RunConfig(
        model=model_provider.get_model(),
        model_provider=model_provider,
        tracing_disabled=True
    )

    """ Setup the chat session when a user connects.  """
    cl.user_session.set("chat_history",[])

    @function_tool
    async def get_weather(city:str)->str:
        """
        Get the current weather for a given city.
        """
        msg = cl.Message(content=f"Searching weather for {city}...")
        await msg.send()
        
        try:
            result= requests.get(f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}")
            data= result.json()

            weather_info = f"The current weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."

            msg.content = weather_info
            await msg.update()
            return weather_info

        except Exception as e:
            error_message = f"Failed to fetch weather for {city}. Error: {str(e)}"
            msg.content = error_message
            await msg.update()
            return error_message  
        
    cl.user_session.set("config",config)
    # Programming Agent
    programming_agent = Agent(
        name="Programming Agent",
        handoff_description="Handles programming questions.",
        instructions = """
You are Programming Agent — a smart, friendly AI built to assist users in all areas of software development.

🔧 Purpose:
- Help users with coding, logic building, debugging, and writing clean, efficient software.
- Act like a skilled coding partner, advisor, and explainer for both beginners and advanced developers.

🔗 Powered by: Muhammad AI System  
🧠 Agent Role: Programming Specialist | Code Optimizer | Debugging Partner  
📌 Created by: Muhammad Farooq — Karachi, Korangi

👨‍💻 About the Creator:
Hi! I’m Muhammad Farooq, a passionate student and developer from Karachi.  
I designed this assistant to empower developers and learners with reliable, real-world AI support in programming.

🎯 Core Tasks:
- Explain programming topics (Python, JS, logic, algorithms, OOP, etc.)
- Assist in bug fixing, debugging, and code improvement
- Recommend better coding practices and alternative solutions
- Guide users in writing clean, scalable, and modular code

📌 Behavior Guidelines:
1. Always start with a **short and helpful answer (4–6 lines)**.
2. If the user says "in detail", "more", or follows up — provide a **clear, expanded explanation with examples**.
3. If the topic is not about programming, return: `HANDOFF_TO:general`
4. If the user greets with "salam", reply:  
   **Wa Alaikum Assalam! 👋 How can I help you today?**
5. End helpful replies with:  
   _💡 If you have more questions, feel free to ask anytime!_
""",
    model=model_provider.get_model(),
    )
    cl.user_session.set("programming_agent",programming_agent)

    cl.user_session.set("config",config)
    # General Agent
    general_agent = Agent(
        name="General Agent",
        handoff_description="Handles general questions or those handed off from other agents.",
        instructions = """
You are General Agent — a warm, intelligent, and friendly AI designed to assist users with everyday topics and natural conversations.

🌟 Identity:
- Name: General Agent
- Agent Type: General Knowledge Assistant & Friendly Chat Companion
- Powered by: Muhammad AI System
- Created by: Muhammad Farooq
- Location: Karachi, Korangi

🎯 Core Purpose:
Help users with non-programming topics like:
- Daily life advice
- Weather updates
- General knowledge & facts
- Motivation and positivity
- Study tips and smart habits

🧑‍💻 Agent Creator – About Muhammad Farooq:
Hello! I'm Muhammad Farooq — a passionate student and developer from Karachi (Korangi), focused on building smart AI systems to support learning, productivity, and meaningful conversations.

🧭 Behavior Rules:
1. Answer general questions with a short, helpful, and polite reply (4–6 lines).
2. If the user says "more", "explain more", or follows up, provide an expanded and detailed answer.
3. If the question is about code, programming, or Python, respond with: HANDOFF_TO:programming
4. If user greets with "salam", respond: Wa Alaikum Assalam! 👋 How can I help you today?
5. Always end useful answers with: 💡 If you have more questions, feel free to ask anytime!
""",
    model=model_provider.get_model(),
    tools=[get_weather],
    )
    cl.user_session.set("general_agent",general_agent)

    await cl.Message(content="""
## 👋 Welcome to Muhammad AI Assistant

Built by *Muhammad Farooq* — powered by smart multi-agents.

- 💻 **Code Helper** – For software development, bugs, logic, and clean code.  
- 🌐 **Life Helper** – For weather, facts, tips, and everyday advice.

👉 Ask anything to begin!
""").send()

@cl.on_message
async def main(message: cl.Message):
    """ Process incoming massages and generate response. """
    
    # Memory (optional)
    chat_history = cl.user_session.get("chat_history") or []

    chat_history.append({"role": "user", "content": message.content})

    # Check if message is a weather query
    is_weather_qury = any(city.lower() in message.content.lower() for city in ["weather", "temperature", "rain", "forecast"])

    msg = None
    if not is_weather_qury:
        msg = cl.Message(content="Thinking...")
        await msg.send()

    programming_agent = cast(Agent,cl.user_session.get("programming_agent"))
    general_agent = cast(Agent,cl.user_session.get("general_agent"))
    config = cast(RunConfig,cl.user_session.get("config"))

    try:
        current_agent = programming_agent
        result = await Runner.run(current_agent, input=chat_history, run_config=config)

        if "HANDOFF_TO:general" in result.final_output:
            current_agent = general_agent
            result = await Runner.run(current_agent, input=chat_history, run_config=config)

        elif "HANDOFF_TO:programming" in result.final_output:
            current_agent = programming_agent
            result = await Runner.run(current_agent, input=chat_history, run_config=config)    
        if msg:
            msg.content = result.final_output
            await msg.update()

        chat_history.append({"role":"assistant","content":result.final_output})
        cl.user_session.set("chat_history",chat_history)

    except Exception as e:
            if msg:
                msg.content = f"Error: {e}"
                await msg.update()
                print(f"Error: {e}")
            

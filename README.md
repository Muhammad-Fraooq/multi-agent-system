# 🤖 Multi-Agent System

A powerful and modular Multi-Agent System built with **OpenAI Agents SDK** and **Chainlit**, leveraging **python-dotenv** for secure configuration. Seamlessly handle diverse queries with intelligent agent routing and an interactive UI — now deployed on **Hugging Face Spaces** with real-time streaming and persistent chat history.

🔗 **Live Demo**: [Try it on Live →](https://huggingface.co/spaces/muhammaddev2007/multi-agent)

---

## 🌟 Features
- 🧠 Specialized agents for general and programming queries
- 🧭 Smart **Triage Agent** for intelligent query routing
- 🌦️ **Weather Tool** – get live weather updates by location or city
- 💬 Real-time **streaming responses**
- 💾 Stores chat history in a **JSON file**
- 🔐 Secure API key management with `.env`
- 🧑‍💻 Chainlit frontend UI
- ☁️ Deployed on Hugging Face Spaces

---

## 🛠 Tech Stack
- 🐍 Python
- 🤖 OpenAI Agents SDK
- 💬 Chainlit
- ☁️ Hugging Face Spaces
- 🌍 Weather API tool (custom built)
- 🧪 python-dotenv for API keys

---

## 🚀 Quick Start

1. **Clone the repo**:
   ```bash
   git clone https://github.com/Muhammad-Fraooq/multi-agent-system.git
   cd multi-agent-system
```

## 2. **Install dependencies**:
   ```bash
   uv install
   ```

## 3. **Set up `.env`**:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

## 4. **Launch the app**:
   ```bash
   chainlit run main.py
   ```
---

## 🧠 How It Works

* All incoming queries are first handled by the **Triage Agent**.
* Based on content, the triage logic routes queries to the right **expert agent**:
  * `general_agent` for non-technical questions
  * `programming_agent` for code-related queries
  * `weather_tool` for weather-related queries
* Uses **streaming output** for better real-time experience.
* Chat sessions are stored in a **local JSON file** (`chat_history.json`) for basic memory.
* Fully **deployed on Hugging Face Spaces** and accessible in the browser.

---

## 📦 Example Weather Tool
You can ask:

> "What's the weather in Karachi?"

The system will:

* Detect the intent using the triage agent
* Use the **weather tool** to fetch real-time data
* Return a friendly temperature and conditions report using city-based lookup

---

## 🤝 Contributing
We welcome contributions! Fork the repo, submit a pull request, or open an issue to suggest improvements or report bugs.

---

## 📄 License
MIT License. See [LICENSE](LICENSE).

---

Built with ❤️ by \[Muhammad Farooq](https://www.linkedin.com/in/muhammad-farooq-developer/)
🔗 Deployed on Hugging Face: [Muhammad Farooq](https://huggingface.co/muhammaddev2007)


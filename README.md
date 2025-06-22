# 🤖 Multi-Agent System

A powerful and modular Multi-Agent System built with **OpenAI Agents SDK** and **Chainlit**, leveraging **python-dotenv** for secure configuration. Seamlessly handle diverse queries with intelligent agent routing and an interactive UI.

## 🌟 Features
- 🧠 Specialized agents for general and programming queries
- 🔄 Dynamic query routing with seamless handoffs
- 💬 User-friendly Chainlit interface
- 🔐 Secure API key management with `.env`

## 🛠 Tech Stack
- 🐍 Python
- 🤖 OpenAI Agents SDK
- 💬 Chainlit
- 🔐 python-dotenv

## 🚀 Quick Start
1. **Clone the repo**:
   ```bash
   git clone https://github.com/Muhammad-Fraooq/multi-agent-system.git
   cd multi-agent-system
   ```
2. **Install dependencies**:
   ```bash
   uv install
   ```
3. **Set up `.env`**:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. **Launch the app**:
   ```bash
   chainlit run main.py
   ```

## 🧠 How It Works
- User queries are routed to either the `general` or `programming` agent based on content.
- Agents leverage tools and memory, with handoffs triggered by `HANDOFF_TO:<agent>` for smooth collaboration.

## 🤝 Contributing
We welcome contributions! Fork the repo, submit a pull request, or open an issue to suggest improvements or report bugs.

## 📄 License
MIT License

---

Built with ❤️ by [Muhammad Farooq] | Powered by OpenAI Agents SDK
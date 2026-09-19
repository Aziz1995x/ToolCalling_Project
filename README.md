# AI Personal Assistant with Tool Calling

This project demonstrates a practical implementation of an AI-powered personal assistant using **LangChain** and **LLMs** (supporting both OpenAI and Google Gemini). The core focus of this project is to showcase **Tool Calling** (Function Calling), where an LLM can decide to execute specific Python functions to interact with the "real world" (simulated here via local CSV files).

## 🚀 Features

- **Multi-Provider LLM Support**: Easily switch between OpenAI and Google Gemini via environment variables.
- **Intelligent Tool Orchestration**: The assistant can autonomously decide which tool to call, extract the necessary arguments, and process the results back into a natural language response.
- **Conversational Memory**: Maintains session-based memory to provide context-aware responses.
- **Deterministic Business Logic**: While the LLM handles the "reasoning," the actual data operations are performed by structured Python tools, ensuring reliability and predictability.
- **Simulated Data Persistence**: Uses local CSV files to track:
  - 📅 **Meetings**: Book and manage appointments.
  - ✅ **Tasks**: Add, update, and list todo items.
  - ✈️ **Flights**: Simulate flight bookings.
  - 🛒 **Orders**: Place simulated shopping orders.

## 🛠️ Technical Architecture

The project follows a modular design to separate concerns:

- `app.py`: The entry point providing a terminal-based chat interface.
- `src/toolcalling_proj/assistant.py`: The orchestrator that implements the tool-calling loop (LLM $\rightarrow$ Tool Execution $\rightarrow$ Final Response).
- `src/toolcalling_proj/llm_client/`: Handles the initialization and caching of the LLM provider.
- `src/toolcalling_proj/tools_manager/`: Contains the `@tool` decorated Python functions that perform the actual data operations.
- `src/toolcalling_proj/memory_management/`: Manages the conversation history.

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ToolCalling_Project
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create a `.env` file in the root directory:
   ```env
   # LLM Provider: "openai" or "gemini"
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4-turbo # or your preferred model

   # API Keys
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional settings
   LLM_TEMPERATURE=0
   ```

## 🖥️ Usage

Start the assistant by running:
```bash
python app.py
```

### Example Interactions:
- *"Book a meeting with Rahul for September 15th at 3 PM."*
- *"Add a task to prepare the LangChain lecture."*
- *"What are my pending tasks?"*
- *"Book a flight to Delhi for tomorrow at 10 AM."*
- *"Order 2 notebooks and 1 blue pen."*

## 📚 Learning Objectives

This project is designed as an educational resource to understand:
1. **Binding Tools**: How to make an LLM aware of available functions.
2. **The Tool Loop**: How to handle `tool_calls` from an LLM and feed `ToolMessage` results back.
3. **Argument Extraction**: How LLMs convert natural language into structured JSON arguments.
4. **State Management**: Combining system prompts, chat history, and tool outputs.

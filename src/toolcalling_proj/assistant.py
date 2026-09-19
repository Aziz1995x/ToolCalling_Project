"""
Connect the LLM, tools, and memory into one simple tool-calling loop.

Teaching flow shown here:
1. Build messages (system prompt + memory + new user message)
2. Ask the LLM
3. If the LLM requests tools → run Python tools → send results back
4. Ask the LLM again for the final natural-language reply
"""

import json
import os
from pathlib import Path
from langchain_core.messages import SystemMessage, ToolMessage

from toolcalling_proj.llm_client import get_llm
from toolcalling_proj.memory_management.memory import add_ai_message, add_user_message, get_messages
from toolcalling_proj.tools_manager.tools import get_all_tools


def load_system_prompt():
    """
    Load the assistant system prompt from prompts/assistant_prompt.txt.

    Returns:
        str: The system prompt text.

    Example:
        prompt = load_system_prompt()
        print(prompt[:80])
    """
    PACKAGE_ROOT = Path(__file__).resolve().parent
    PROMPT_PATH = PACKAGE_ROOT / "prompts" / "assistant_prompt.txt"
    # project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # prompt_path = os.path.join(project_root, "prompts", "assistant_prompt.txt")

    with open(str(PROMPT_PATH), "r", encoding="utf-8") as file:
        return file.read().strip()


def create_assistant(memory):
    """
    Create a simple callable assistant that uses tool calling + memory.

    Args:
        memory (list): Conversation history list from src.memory.create_memory().

    Returns:
        function: A chat(user_message) function that returns the assistant reply.

    Example:
        from src.memory import create_memory
        memory = create_memory()
        chat = create_assistant(memory)
        print(chat("Show me my pending tasks."))
    """
    llm = get_llm()
    tools = get_all_tools()

    # Bind tools so the LLM can choose when to call them.
    llm_with_tools = llm.bind_tools(tools)

    # Map tool name → tool object for easy lookup during execution.
    tools_by_name = {tool.name: tool for tool in tools}

    system_prompt = load_system_prompt()

    def chat(user_message):
        """
        Process one user message and return the assistant's final reply.

        Args:
            user_message (str): Text typed by the user.

        Returns:
            str: Final assistant response after any tool calls.
        """
        # Save the user message into conversational memory.
        add_user_message(memory, user_message)

        # Build the full message list for this turn.
        messages = [SystemMessage(content=system_prompt)] + get_messages(memory)

        # First LLM call — may return normal text OR one/more tool calls.
        response = llm_with_tools.invoke(messages)

        # Simple loop: keep running tools until the LLM stops requesting them.
        # This also supports multi-tool requests in one user message.
        while getattr(response, "tool_calls", None):
            messages.append(response)

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id", tool_name)

                # Educational logging — show learners what the LLM decided.
                print("\n[Tool Call]")
                print(f"Tool: {tool_name}")
                print("Arguments:")
                print(json.dumps(tool_args, indent=4))

                selected_tool = tools_by_name.get(tool_name)
                if selected_tool is None:
                    tool_result = f"Unknown tool: {tool_name}"
                else:
                    # Run the real Python function (deterministic business logic).
                    tool_result = selected_tool.invoke(tool_args)

                print("\n[Tool Result]")
                print(tool_result)
                print()

                # Send the tool result back to the LLM.
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id,
                    )
                )

            # Second (or later) LLM call — now it can write the final answer.
            response = llm_with_tools.invoke(messages)

        final_text = response.content
        if isinstance(final_text, list):
            # Some models may return content blocks; keep only text pieces.
            parts = []
            for block in final_text:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                else:
                    parts.append(str(block))
            final_text = "".join(parts)

        final_text = (final_text or "").strip()
        if not final_text:
            final_text = "I completed the request, but I do not have more details to share."

        # Save only the final assistant reply into memory (not tool internals).
        add_ai_message(memory, final_text)
        return final_text

    return chat

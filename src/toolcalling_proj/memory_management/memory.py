"""
Simple conversational memory for the assistant.

We store chat history as a plain Python list of LangChain messages.
No complex memory classes — just append and reuse.
"""

from langchain_core.messages import AIMessage, HumanMessage


def create_memory():
    """
    Create an empty conversation memory list.

    Returns:
        list: An empty list that will store HumanMessage and AIMessage objects.

    Example:
        memory = create_memory()
        add_user_message(memory, "Hello")
        add_ai_message(memory, "Hi there!")
    """
    return []


def add_user_message(memory, text):
    """
    Append a user message to conversation memory.

    Args:
        memory (list): The conversation history list.
        text (str): The user's message text.

    Returns:
        None
    """
    memory.append(HumanMessage(content=text))


def add_ai_message(memory, text):
    """
    Append an assistant message to conversation memory.

    Args:
        memory (list): The conversation history list.
        text (str): The assistant's reply text.

    Returns:
        None
    """
    memory.append(AIMessage(content=text))


def get_messages(memory):
    """
    Return the current conversation messages.

    Args:
        memory (list): The conversation history list.

    Returns:
        list: The same list of messages (for readability in the lecture).
    """
    return memory

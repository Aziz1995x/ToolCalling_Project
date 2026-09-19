"""
Terminal chat interface for the AI Personal Assistant.

Run:
    python app.py

Type exit or quit to leave the chat.
"""

from toolcalling_proj.assistant import create_assistant
from toolcalling_proj.memory_management.memory import create_memory


def main():
    """
    Start the terminal chat loop.

    Creates conversation memory, builds the assistant, then repeatedly
    reads user input and prints the assistant response.

    Returns:
        None
    """
    print("=" * 40)
    print("AI PERSONAL ASSISTANT")
    print("=" * 40)
    print("Type 'exit' or 'quit' to leave.\n")

    # One memory object is reused for the whole session.
    memory = create_memory()
    chat = create_assistant(memory)

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_message:
            continue

        if user_message.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            reply = chat(user_message)
            print(f"\nAssistant: {reply}\n")
        except Exception as error:
            # Keep errors beginner-friendly and visible in the terminal.
            print("\nAssistant: Sorry, something went wrong while processing your request.")
            print(f"Details: {error}\n")


if __name__ == "__main__":
    main()

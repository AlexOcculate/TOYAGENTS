# No imports needed — we just manage a list of dicts.


# ContextManager handles the conversation history window.
# In a real agent, this controls token limits and sliding windows.
class ContextManager:

    # Constructor — max_messages defines the sliding window size.
    def __init__(self, max_messages=20):
        self.max_messages = max_messages
        self.messages = []  # List of {"role": str, "content": str}

    # Add a message to the context. Trims if over limit.
    def add(self, role, content):

        # Append the new message.
        self.messages.append({"role": role, "content": content})

        # If we exceed the window, drop the oldest (keep system msg if present).
        while len(self.messages) > self.max_messages:

            # Don't remove index 0 if it's a system message.
            if self.messages[1].get("role") == "system":
                break

            self.messages.pop(1)

    # Return the full message list (ready to send to the LM).
    def get_context(self):
        return list(self.messages)

    # Clear all messages (useful for resetting the conversation).
    def clear(self):
        self.messages = []

    # Return a human-readable summary of current context size.
    def summary(self):
        return f"Context: {len(self.messages)}/{self.max_messages} messages"

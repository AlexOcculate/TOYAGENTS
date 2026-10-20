# ToolRegistry holds all available tools the agent can use.
class ToolRegistry:

    # Constructor initializes an empty dict to store tools.
    def __init__(self):
        self._tools = {}  # name -> {"description": str, "fn": callable}

    # Register a tool by name, description, and callable function.
    def register(self, name, description, fn):
        self._tools[name] = {"description": description, "fn": fn}

    # Execute a tool by name with keyword arguments.
    # Returns the result or raises if tool not found.
    def execute(self, name, **kwargs):

        # Check if the tool exists.
        if name not in self._tools:
            raise ValueError(f"Unknown tool: '{name}'")
        # Call the underlying function with the provided args.
        return self._tools[name]["fn"](**kwargs)

    # List all registered tool names (useful for debugging).
    def list_tools(self):
        return list(self._tools.keys())


# ACTUAL TOOL IMPLEMENTATIONS (pure Python, no deps) ---


# Add two numbers.
def tool_add(a, b):
    return a + b


# Subtract b from a.
def tool_subtract(a, b):
    return a - b


# Factory function that builds a fully-wired ToolRegistry.
# Memory tools are injected because they need a PersistentMemory instance.
def build_tool_registry(memory):

    # Create a fresh registry.
    registry = ToolRegistry()

    # Register the math tools.
    registry.register("add", "Adds two integers", tool_add)
    registry.register("subtract", "Subtracts b from a", tool_subtract)

    # Register memory tools (they close over the `memory` instance).
    registry.register(
        "memory_store",
        "Stores a key-value pair in persistent memory",
        lambda key, value: _store(memory, key, value),
    )
    registry.register(
        "memory_recall",
        "Recalls a value by key from persistent memory",
        lambda key: _recall(memory, key),
    )
    registry.register(
        "memory_list", "Lists all stored memories", lambda: _list_all(memory)
    )

    # Return the fully configured registry.
    return registry


# Private helper — store a memory entry.
def _store(memory, key, value):
    memory.store(key, value)
    return f"Stored '{key}' = '{value}'"


# Private helper — recall a memory entry.
def _recall(memory, key):
    result = memory.recall(key)
    if result is None:
        return f"No memory found for '{key}'"
    return f"'{key}' = '{result}'"


# Private helper — list all memories.
def _list_all(memory):
    entries = memory.get_all()
    if not entries:
        return "Memory is empty."
    return "\n".join(f"  {k} = {v}" for k, v in entries.items())

"""
ToyAgentNoBrain/
├── main.py
└── Harness/
    ├── __init__.py
    ├── context_management.py
    ├── guardrails.py
    ├── lm_call.py
    ├── loop.py
    ├── persistent_memory.py
    ├── recovery.py
    ├── tools.py
    └── trace_logger.py
"""

# Add the parent directory to sys.path so we can import Harness.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the factory from our harness.
from Harness.loop import create_agent


#  Main demo function — simulates a multi-turn conversation.
def main():

    print("=" * 60)
    print("  ToyAgentNoBrain — Educational Agent Demo")
    print("=" * 60)

    # Create the agent (uses agent_memory.json in the current directory)
    agent = create_agent(memory_filepath="agent_memory.json")
    # agent.lm = ChaoticLM()  # ← that's it. Harness handles the chaos.

    # A series of test inputs to demonstrate each capability.
    demo_inputs = [
        "add 3 and 7",
        "subtract 10 and 4",
        "remember cat is orange",
        "remember dog is loyal",
        "what do you remember about cat",
        "list memories",
        "hello there friend",
        "multiply 6 and 9",
    ]

    print(f"\nRegistered tools:\n\t{agent.tools.list_tools()}")
    print(f"\nGuardrails:")
    print(f"\n\t- Forbidden patterns: {agent.guardrails.forbidden_patterns}")
    print(f"\n\t- Maximum input length: {agent.guardrails.max_input_length}")
    print(f"\n\t- Maximum iterations: {agent.guardrails.max_iterations}")
    print(f"\nSystem message:")
    print(f"\n\t{agent.context.messages[0]['content']}")

    print("-" * 60)

    for user_msg in demo_inputs:
        print(f"\n👤 User: {user_msg}")
        response = agent.run(user_msg)
        print(f"🤖 Agent: {response}")

    # Show the context summary at the end.
    print("\n" + "-" * 60)
    print(f"Final context status: {agent.context.summary()}")

    # Show any recovery failures (should be empty in normal operation).
    if agent.recovery.get_failure_log():
        print("Recovery log:")
        for entry in agent.recovery.get_failure_log():
            print(
                f"  Attempt {entry['attempt']}: {entry['error']} ({entry['context']})"
            )
    else:
        print("Recovery log: (no failures)")

    print("\n" + "=" * 60)
    print("  Done. Memory persisted to agent_memory.json")
    print("=" * 60)


# Line 52: Standard Python entry-point guard.
if __name__ == "__main__":
    main()
    print("\nExiting ToyAgentNoBrain. Goodbye!\n")
    print("=" * 60)

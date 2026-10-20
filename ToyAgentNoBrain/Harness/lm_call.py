# Line 1:  Import json to parse structured tool-call responses.
import json


# Line 4:  SimulatedLM — mimics a real LLM using keyword matching.
class SimulatedLM:

    # Line 7: Constructor.
    def __init__(self, model_name="ToyLLM-v0"):
        self.model_name = model_name

    # Line 10: Main entry point. Receives full message history, returns a response dict.
    def generate(self, messages):
        # ──────────────────────────────────────────────────────────────
        # KEY FIX: If a tool result already exists AFTER the last user
        # message, the work is done — just relay it as the final answer.
        # This prevents the infinite re-call loop.
        # ──────────────────────────────────────────────────────────────

        # Line 17: Find the index of the last user message.
        last_user_idx = -1
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "user":
                last_user_idx = i
                break

        # Line 23: Check if any tool result exists AFTER that user message.
        has_tool_result = False
        for i in range(last_user_idx + 1, len(messages)):
            if messages[i]["role"] == "tool":
                has_tool_result = True
                break

        # Line 29: If yes → the tool already ran. Return its output as final answer.
        if has_tool_result:
            last_tool_content = ""
            for msg in reversed(messages):
                if msg["role"] == "tool":
                    last_tool_content = msg["content"]
                    break
            return {"content": last_tool_content, "tool_call": None}

        # ──────────────────────────────────────────────────────────────
        # No tool result yet → decide what to do (the "thinking" phase).
        # ──────────────────────────────────────────────────────────────

        # Line 40: Grab the last user message text.
        last_user_msg = (
            messages[last_user_idx]["content"].lower() if last_user_idx >= 0 else ""
        )

        # Line 42: --- DECISION TREE ---

        if "add" in last_user_msg:
            nums = self._extract_numbers(last_user_msg)
            return {
                "content": None,
                "tool_call": {
                    "name": "add",
                    "arguments": json.dumps({"a": nums[0], "b": nums[1]}),
                },
            }

        if "subtract" in last_user_msg:
            nums = self._extract_numbers(last_user_msg)
            return {
                "content": None,
                "tool_call": {
                    "name": "subtract",
                    "arguments": json.dumps({"a": nums[0], "b": nums[1]}),
                },
            }

        if (
            "remember" in last_user_msg
            and "about" not in last_user_msg
            and "recall" not in last_user_msg
        ):
            parts = last_user_msg.replace("remember", "").strip().split(" is ", 1)
            key = parts[0].strip() if len(parts) > 0 else "unknown"
            value = parts[1].strip() if len(parts) > 1 else "nothing"
            return {
                "content": None,
                "tool_call": {
                    "name": "memory_store",
                    "arguments": json.dumps({"key": key, "value": value}),
                },
            }

        if ("remember" in last_user_msg or "recall" in last_user_msg) and (
            "about" in last_user_msg or "recall" in last_user_msg
        ):
            key = last_user_msg.replace("what do you remember about", "").strip()
            key = key.replace("recall", "").strip()
            return {
                "content": None,
                "tool_call": {
                    "name": "memory_recall",
                    "arguments": json.dumps({"key": key}),
                },
            }

        if "list" in last_user_msg and "memor" in last_user_msg:
            return {
                "content": None,
                "tool_call": {"name": "memory_list", "arguments": json.dumps({})},
            }

        # Default: conversational response, no tool needed.
        rtn = {
            "content": f"[{self.model_name}] I heard: '{last_user_msg}'. "
            f"Try 'add 3 and 5', 'remember cat is orange', or 'list memories'.",
            "tool_call": None,
        }
        return rtn

    # Line 92: Helper — extract first two integers from a string.
    def _extract_numbers(self, text):
        nums = []
        for word in text.split():
            try:
                nums.append(int(word))
            except ValueError:
                pass
            if len(nums) == 2:
                break
        while len(nums) < 2:
            nums.append(0)
        return nums[0], nums[1]


class ChaoticLM:
    """Returns random garbage. Tests recovery + guardrails."""

    def __init__(self):
        self.call_count = 0

    def generate(self, messages):
        self.call_count += 1
        import random

        choices = [
            {
                "content": None,
                "tool_call": {"name": "nonexistent_tool", "arguments": "{}"},
            },
            {"content": "I'm feeling chaotic today.", "tool_call": None},
            {
                "content": None,
                "tool_call": {"name": "add", "arguments": "not json at all"},
            },
        ]
        return random.choice(choices)


class LazyLM:
    """Never calls tools. Just talks. Tests that the loop terminates."""

    def generate(self, messages):
        return {"content": "[LazyLM] I refuse to use tools.", "tool_call": None}


class InfiniteLoopLM:
    """Always calls a tool. Tests the iteration guardrail."""

    def generate(self, messages):
        return {
            "content": None,
            "tool_call": {"name": "add", "arguments": '{"a": 1, "b": 1}'},
        }

# micro_harness.py — The entire agent in 50 lines. No subfolder needed.


class LM:
    """Simulated brain. Replace this to plug in a real model."""

    def generate(self, messages):
        last = messages[-1]["content"].lower()
        if "add" in last:
            nums = [int(w) for w in last.split() if w.isdigit()]
            return {"tool_call": {"name": "add", "args": {"a": nums[0], "b": nums[1]}}}
        return {"content": f"Echo: {last}", "tool_call": None}


class Harness:
    """The body. Works with ANY LM that has .generate(messages)."""

    def __init__(self, lm):
        self.lm = lm  # ← The ONLY place the LM touches the harness
        self.context = []
        self.max_iter = 5

    def tools(self, name, args):
        if name == "add":
            return args["a"] + args["b"]
        raise ValueError(f"Unknown tool: {name}")

    def run(self, user_input):
        # Guardrail
        if len(user_input) > 200:
            return "[BLOCKED] Too long"
        self.context.append({"role": "user", "content": user_input})

        for _ in range(self.max_iter):
            # Think
            resp = self.lm.generate(self.context)

            # Act or Done?
            if resp.get("tool_call") is None:
                answer = resp["content"]
                self.context.append({"role": "assistant", "content": answer})
                return answer

            # Execute tool
            tc = resp["tool_call"]
            result = self.tools(tc["name"], tc["args"])
            self.context.append({"role": "tool", "content": str(result)})

        return "[STOPPED] Max iterations"


# --- Run it ---
agent = Harness(LM())
print(agent.run("add 3 and 7"))  # → 10
print(agent.run("hello world"))  # → Echo: hello world

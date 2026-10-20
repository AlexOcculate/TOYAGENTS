# Line 1:  Import everything we need from sibling modules.
from .lm_call import SimulatedLM
from .tools import build_tool_registry
from .persistent_memory import PersistentMemory
from .context_management import ContextManager
from .recovery import RecoveryHandler
from .guardrails import Guardrails
from .trace_logger import TraceLogger  # ← NEW


# Line 9:  AgentLoop — the orchestrator.
class AgentLoop:

    # Line 12: Constructor.
    def __init__(self, memory_filepath="agent_memory.json", verbose_trace=True):
        self.lm = SimulatedLM()
        self.memory = PersistentMemory(memory_filepath)
        self.tools = build_tool_registry(self.memory)
        self.context = ContextManager(max_messages=20)
        self.recovery = RecoveryHandler(max_retries=3)
        self.guardrails = Guardrails()
        self.trace = TraceLogger(verbose=verbose_trace)  # ← NEW

        self.context.add("system", "You are ToyAgentNoBrain. Use tools when helpful.")

    # Line 24: Main entry point.
    def run(self, user_input):
        # STEP 1: Guardrail check
        valid, reason = self.guardrails.validate_input(user_input)
        self.trace.log(
            "guardrails", "input_check", f"'{user_input[:30]}' → valid={valid}"
        )
        if not valid:
            return f"[BLOCKED] {reason}"

        # STEP 2: Add to context
        self.context.add("user", user_input)
        self.trace.log("context", "message_added", f"role=user, len={len(user_input)}")

        # STEP 3: Agentic loop
        iteration = 0
        while True:
            iteration += 1

            ok, reason = self.guardrails.check_iteration_limit(iteration)
            if not ok:
                self.trace.log("loop", "stopped", f"{reason}")
                return f"[STOPPED] {reason}"

            # STEP 4: LM call
            messages = self.context.get_context()
            self.trace.log("lm", "generate_call", f"messages={len(messages)}")
            response = self.recovery.execute(
                fn=lambda: self.lm.generate(messages),
                fallback={"content": "[ERROR] LM failed.", "tool_call": None},
                context="lm_generate",
            )

            # STEP 5: Validate output
            valid, reason = self.guardrails.validate_output(response)
            self.trace.log("guardrails", "output_check", f"valid={valid}")
            if not valid:
                return f"[MALFORMED RESPONSE] {reason}"

            # STEP 6: Tool call or final answer?
            if response["tool_call"] is None:
                self.context.add("assistant", response["content"])
                self.trace.log("loop", "final_answer", f"'{response['content'][:40]}'")
                return response["content"]

            # STEP 7: Execute tool
            tool_name = response["tool_call"]["name"]
            import json

            args = json.loads(response["tool_call"]["arguments"])
            self.trace.log("tools", "execute", f"{tool_name}({args})")

            try:
                result = self.tools.execute(tool_name, **args)
            except Exception as e:
                self.trace.log("recovery", "tool_error", f"{tool_name}: {e}")
                self.context.add("assistant", f"Tool '{tool_name}' failed: {e}")
                continue

            # STEP 8: Feed result back
            self.context.add("tool", f"[{tool_name}] {result}")
            self.trace.log("tools", "result", f"{tool_name} → {result}")


# Line 75: Factory.
def create_agent(memory_filepath="agent_memory.json", verbose_trace=True):
    return AgentLoop(memory_filepath=memory_filepath, verbose_trace=verbose_trace)

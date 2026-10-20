# 🧸 ToyAgentNoBrain

> **A zero-dependency, educational Python project that demonstrates how AI Agents work — without using a single LLM.**

---

## 🧠 First Things First: What Even *Is* an Agent Harness?

You've probably seen the word **"harness"** everywhere in AI agent discussions and thought: *"Okay... but what does that actually mean?"*

Here's the short version.

### An AI Agent Has Two Parts



## What Is This?

An **AI Agent** is a program that can *think*, *decide*, and *act* in a loop until a task is complete. Most tutorials show you agents by calling OpenAI or Anthropic APIs, which makes it hard to see what the **agent itself** actually does versus what the **model** does.

**ToyAgentNoBrain separates the two.**

| Layer                  | What it does                                          | In this project                                     |
| ---------------------- | ----------------------------------------------------- | --------------------------------------------------- |
| **The Brain (LLM)**    | Receives context, decides what to do next             | A simple keyword-matching simulator (`SimulatedLM`) |
| **The Body (Harness)** | Manages memory, tools, safety, recovery, and the loop | 7 small files in `Harness/`                         |

You can swap the brain for a real LLM by changing **one file**. The body never changes. That's the point.

---

## Why Does This Exist?

If you've ever read about "agentic AI" and felt lost, it's probably because:

- You need an API key to test anything
- The LLM's "thinking" is opaque — you can't see *why* it chose a tool
- The agent infrastructure (memory, guardrails, recovery) gets buried in boilerplate

This project strips all of that away. You get:

- ✅ A **runnable agent** with zero setup (no API keys, no `pip install`)
- ✅ **Visible decisions** — the simulated LM uses simple rules you can read
- ✅ **Isolated components** — each concern lives in its own file
- ✅ **A trace logger** that prints every step of the loop in color
- ✅ **Adversarial tests** that prove the harness protects the system even with a "broken" brain

Think of it as an **X-ray of an agent**: you see the skeleton, the wiring, and the safety systems — without the noise of a real model.

---

## Folder Structure
```text
ToyAgentNoBrain/
 ├── main.py                      # Entry point & demo driver
 └── Harness/
      ├── init.py                 # Package marker
      ├── context_management.py   # Short-term memory (conversation window)
      ├── guardrails.py           # Input/output validation & safety limits
      ├── lm_call.py              # Simulated LLM (the "brain")
      ├── loop.py                 # Orchestrator — wires everything together
      ├── persistent_memory.py    # Long-term memory (JSON file on disk) 
      ├── recovery.py             # Retry logic & fault tolerance 
      ├── tools.py                # Tool registry & implementations 
      └── trace_logger.py         # Colored step-by-step execution log
```

---

## Dependencies

### External

**None.** This project uses only the Python standard library:

| Module | Used in                                         | Purpose                     |
| ------ | ----------------------------------------------- | --------------------------- |
| `json` | `lm_call.py`, `persistent_memory.py`, `loop.py` | Serialize/deserialize data  |
| `os`   | `persistent_memory.py`, `main.py`               | File path handling          |
| `time` | `recovery.py`, `trace_logger.py`                | Backoff delays & timestamps |

No `pip install`. No virtual environment. No API keys.

### Internal (Project Files)
```text
main.py
 └── imports → Harness/loop.py 
                ├── imports → Harness/lm_call.py 
                ├── imports → Harness/tools.py 
                ├── imports → Harness/persistent_memory.py 
                ├── imports → Harness/context_management.py 
                ├── imports → Harness/recovery.py 
                ├── imports → Harness/guardrails.py 
                └── imports → Harness/trace_logger.py

 
`loop.py` is the **only** file that imports all other harness components. It is the composition root.
```

---

## Execution

### Requirements

- Python 3.8 or later
- That's it.

### Run the Demo

```bash
# Navigate to the project root
cd ToyAgentNoBrain

# Run
python main.py
```

## Expected Output
```text
============================================================
  ToyAgentNoBrain — Educational Agent Demo
============================================================

Registered tools: ['add', 'subtract', 'memory_store', 'memory_recall', 'memory_list']
------------------------------------------------------------

👤 User: add 3 and 7
  [01]   guardrails │ input_check               │ 'add 3 and 7' → valid=True
  [02]      context │ message_added             │ role=user, len=11
  [03]           lm │ generate_call             │ messages=2
  [04]   guardrails │ output_check              │ valid=True
  [05]        tools │ execute                   │ add({'a': 3, 'b': 7})
  [06]        tools │ result                    │ add → 10
  [07]           lm │ generate_call             │ messages=3
  [08]   guardrails │ output_check              │ valid=True
  [09]         loop │ final_answer              │ '[add] 10'
🤖 Agent: [add] 10

👤 User: remember cat is orange
  ...
🤖 Agent: [memory_store] Stored 'cat' = 'orange'

👤 User: what do you remember about cat
  ...
🤖 Agent: [memory_recall] 'cat' = 'orange'

👤 User: list memories
  ...
🤖 Agent: [memory_list]   cat = orange
                           dog = loyal

👤 User: hello there friend
  ...
🤖 Agent: [ToyLLM-v0] I heard: 'hello there friend'. Try 'add 3 and 5'...

------------------------------------------------------------
Final context status: Context: 14/20 messages
Recovery log: (no failures)

============================================================
  Done. Memory persisted to agent_memory.json
============================================================
```

> The colored trace lines (green = valid, red = blocked, yellow = error) appear in your terminal.


## Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (entry point / demo driver)                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │  agent.run(user_input)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Harness/loop.py                             │
│                  (AgentLoop — the orchestrator)                  │
│                                                                  │
│   ┌────────────┐    ┌───────────────┐    ┌───────────────────┐   │
│   │ Guardrails │───▶│ Context Mgr   │───▶│     LM Call       │   │
│   │ (validate) │    │ (window mgmt) │    │  (SimulatedLM)    │   │
│   └────────────┘    └───────────────┘    └─────────┬─────────┘   │
│                                                    │             │
│                              ┌─────────────────────┘             │
│                              ▼                                   │
│               ┌────────────────────────┐                         │
│               │   Recovery Handler     │                         │
│               │  (retry + fallback)    │                         │
│               └────────────┬───────────┘                         │
│                            │                                     │
│                            ▼                                     │
│               ┌────────────────────────┐    ┌────────────────┐   │
│               │     Tool Registry      │───▶│ Persistent     │   │
│               │ (add, subtract,        │    │ Memory         │   │
│               │  memory_store, etc.)   │    │ (JSON on disk) │   │
│               └────────────────────────┘    └────────────────┘   │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │              Trace Logger (observes every step)          │   │
│   └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**Key principle**: The LM (lm_call.py) is a leaf node. It receives messages and returns a response. 
It knows nothing about tools, memory, guardrails, or the loop. To use a real LLM, you replace this one file — nothing else changes.


## State Machine Diagram
The agent loop is a _finite state machine_. Each user input drives it through these states:
```text
                         ┌──────────────────────────────────────────────┐
                         │                                              │
                         ▼                                              │
                   ┌───────────┐                                  ┌──────────┐
                   │   IDLE    │                                  │   DONE   │
                   └─────┬─────┘                                  └──────────┘
                         │ user_input arrives                           ▲
                         ▼                                              │
                   ┌───────────┐   invalid    ┌───────────┐             │
                   │GUARDRAILS ├─────────────▶│  BLOCKED  │             │
                   └─────┬─────┘              └───────────┘             │
                         │ valid                                        │
                         ▼                                              │
                   ┌───────────┐                                  ┌───────────┐
                   │ THINKING  │  (LM is called)                  │ OBSERVING │
                   └─────┬─────┘                                  └─────┬─────┘
                         │                                              │
                 ┌───────┴────────┐                                     │
                 │                │                                     │
          no tool_call       tool_call                                  │
                 │                │                                     │
                 ▼                ▼                                     │
           ┌──────────┐     ┌──────────┐                                │
           │   DONE   │     │  ACTING  │────────────────────────────────┘
           └──────────┘     └────┬─────┘
                                 │ tool execution fails
                                 ▼
                           ┌────────────┐
                           │ RECOVERING │──▶ back to THINKING (or DONE if max retries)
                           └────────────┘

         ⚠️  Any state → iteration limit reached → STOPPED
```


## State Descriptions

| State      | What happens                              | Component responsible    |
| ---------- | ----------------------------------------- | ------------------------ |
| IDLE       | Waiting for user input                    | main.py                  |
| GUARDRAILS | Validate input length, forbidden patterns | guardrails.py            |
| BLOCKED    | Input rejected, return error to user      | guardrails.py            |
| THINKING   | Call the LM with current context          | lm_call.py + recovery.py |
| ACTING     | Execute the chosen tool                   | tools.py                 |
| OBSERVING  | Feed tool result back into context        | context_management.py    |
| RECOVERING | Tool failed, log error, retry or abort    | recovery.py              |
| DONE       | Final answer returned to user             | loop.py                  |
| STOPPED    | Max iterations reached (safety net)       | guardrails.py            |



## File Reference

### `main.py`

**Role:** Entry point and demo driver.

Creates the agent, feeds it a series of test inputs, and prints the conversation. This is what you run. It contains no agent logic — only "say hello to the agent" code.

**For non-IT readers:** Think of this as the person talking to the robot. They say things; the robot responds. The file just scripts the conversation.

---

### `Harness/__init__.py`

**Role:** Python package marker.

Tells Python that `Harness/` is a module you can import from. Contains no logic.

---

### `Harness/context_management.py`

**Role:** Short-term memory (the conversation window).

Maintains a list of messages (who said what, in what order). Enforces a maximum window size so the context doesn't grow forever. In a real agent, this is where you'd count tokens and trim old messages to fit within an LLM's context window.

**For non-IT readers:** This is the agent's "short-term memory" — like your working memory when someone is talking to you. You remember the last few sentences, but not the entire conversation from 3 hours ago.

---

### `Harness/guardrails.py`

**Role:** Safety checks (input validation, output validation, iteration limits).

Three jobs:
1. **Before** the LM sees anything: reject inputs that are too long or contain dangerous patterns.
2. **After** the LM responds: verify the response is well-formed.
3. **During** the loop: stop the agent if it's been looping too many times (prevents infinite loops).

**For non-IT readers:** These are the seatbelts and airbags. They don't drive the car, but they keep you safe when something goes wrong.

---

### `Harness/lm_call.py`

**Role:** The simulated "brain."

This is the **only file that simulates intelligence**. It uses simple keyword matching to decide what to do:
- Sees "add" → returns a tool call for addition
- Sees "remember X is Y" → returns a tool call to store memory
- Sees nothing special → returns a conversational reply

**This is the file you replace** when you want to plug in a real LLM (OpenAI, Anthropic, a local model, etc.). The interface is one method: `generate(messages) → dict`. Everything else in the project stays the same.

**For non-IT readers:** This is where the "thinking" happens. In this toy, it's very simple (if you say "add", I add). In a real agent, this would be GPT-4 or Claude doing the reasoning.

---

### `Harness/loop.py`

**Role:** The orchestrator (composition root).

Wires all other components together and runs the core cycle:

```
Receive input → Validate → Think (LM) → Act (Tool) → Observe (Context) → Repeat or Done
```

This is the only file that imports all other harness files. If you understand this file, you understand how an agent works.

**For non-IT readers:** This is the "conductor" of an orchestra. It doesn't play any instrument itself — it tells each musician when to play and in what order.

---

### `Harness/persistent_memory.py`

**Role:** Long-term memory (survives restarts).

Stores key-value pairs in a JSON file on disk. The agent can "remember" things across sessions. When you close the program and reopen it, the memories are still there.

**For non-IT readers:** This is like a notebook the agent keeps. Even if it "falls asleep" (the program closes), when it wakes up, it can flip through its notes.

---

### `Harness/recovery.py`

**Role:** Fault tolerance (retry with backoff).

Wraps risky operations (like calling the LM) in a retry loop. If the call fails, it waits a bit and tries again — up to a maximum number of times. If all retries fail, it returns a safe fallback instead of crashing.

**For non-IT readers:** This is like calling a restaurant that's not answering. You try once, wait 5 seconds, try again, wait 10 seconds, try one more time. If it still doesn't answer, you order from a different place (the fallback). You don't just give up and starve.

---

### `Harness/tools.py`

**Role:** The action space (what the agent can *do*).

A registry of named functions the agent can call. In this project: `add`, `subtract`, `memory_store`, `memory_recall`, `memory_list`. Adding a new tool is one line: `registry.register("name", "description", function)`.

**For non-IT readers:** These are the agent's hands. The brain (LM) decides *what* to do; the tools are how it actually *does* it. In this toy, the hands can add numbers and write in a notebook. In a real agent, the hands might send emails, query databases, or control robots.

---

### `Harness/trace_logger.py`

**Role:** Colored step-by-step execution log.

Prints every decision the agent makes, with color coding:
- 🟩 **Light green background** = validation passed (`valid=True`)
- 🔴 **Light red background** = validation failed / blocked
- 🟡 **Light yellow background** = error or failure detected
- Component names are color-coded by type (red = guardrails, cyan = context, magenta = LM, etc.)

This makes the invisible visible. You can *watch* the state machine execute in real time.

**For non-IT readers:** This is like a black box recorder on an airplane. It doesn't affect how the plane flies, but if something goes wrong (or you just want to understand what happened), you can replay the entire flight step by step.

---

## Extending: Swapping in a Real LLM

To use a real model, replace **only** `Harness/lm_call.py`:

```python
# Before (simulated):
class SimulatedLM:
    def generate(self, messages):
        # keyword matching...

# After (real — example with OpenAI):
import openai

class OpenAILM:
    def __init__(self, model="gpt-4"):
        self.client = openai.OpenAI()
        self.model = model

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[...],  # your tool schemas
        )
        # Parse and return in the same format:
        # {"content": str or None, "tool_call": dict or None}
```

Then in `loop.py`, change one line:

```python
# Before:
self.lm = SimulatedLM()

# After:
self.lm = OpenAILM()
```

**That's it.** The harness doesn't care what's inside the brain. It only cares that `generate(messages)` returns a dict with `content` and/or `tool_call`.

---

## License

MIT — use it, break it, learn from it.
```

---

## Notes on the README

| Design choice                                      | Why                                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------------------- |
| "For non-IT readers" callouts in each file section | Keeps the document accessible without dumbing down the technical content     |
| State machine table after the diagram              | Gives a *name* to each state so readers can reference them in discussion     |
| The "Swapping in a Real LLM" section at the end    | Proves the core thesis: harness ≠ model. One file swap. Done.                |
| No badges, no CI references                        | This is a toy project. Badges would imply infrastructure that doesn't exist. |
| `trace_logger.py` (not `trace.py`)                 | Matches your specified folder structure exactly                              |
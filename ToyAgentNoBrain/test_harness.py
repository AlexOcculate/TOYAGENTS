"""
Run with: python test_harness.py
No pytest needed — pure assert + print.
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Harness.loop import create_agent
from Harness.lm_call import ChaoticLM, InfiniteLoopLM, LazyLM


def test_guardrail_blocks_long_input():
    agent = create_agent(memory_filepath="/tmp/test_mem.json")
    result = agent.run("x" * 1000)
    assert "[BLOCKED]" in result
    print("✓ Long input blocked")


def test_infinite_loop_lm_stops():
    agent = create_agent(memory_filepath="/tmp/test_mem.json")
    agent.lm = InfiniteLoopLM()
    result = agent.run("add 1 and 1")
    assert "[STOPPED]" in result
    print("✓ Infinite loop LM stopped at iteration cap")


def test_lazy_lm_returns_immediately():
    agent = create_agent(memory_filepath="/tmp/test_mem.json")
    agent.lm = LazyLM()
    result = agent.run("add 5 and 5")
    assert "refuse" in result.lower()
    print("✓ Lazy LM returned without tool call")


def test_chaotic_lm_doesnt_crash():
    agent = create_agent(memory_filepath="/tmp/test_mem.json")
    agent.lm = ChaoticLM()
    # Should NOT raise, even with garbage responses
    for _ in range(5):
        result = agent.run("add 1 and 2")
        assert isinstance(result, str)
    print("✓ Chaotic LM handled without crash")


def test_memory_persists_across_agents():
    # Agent 1 stores
    a1 = create_agent(memory_filepath="/tmp/test_mem.json")
    a1.run("remember secret is 42")
    # Agent 2 (fresh instance) recalls
    a2 = create_agent(memory_filepath="/tmp/test_mem.json")
    result = a2.run("what do you remember about secret")
    assert "42" in result
    print("✓ Memory persists across agent instances")


if __name__ == "__main__":
    test_guardrail_blocks_long_input()
    test_infinite_loop_lm_stops()
    test_lazy_lm_returns_immediately()
    test_chaotic_lm_doesnt_crash()
    test_memory_persists_across_agents()
    print("\n✅ All tests passed.")

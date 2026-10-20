# No imports needed.


# Guardrails enforce safety and sanity checks on inputs and outputs.
class Guardrails:

    # Constructor — configures limits and forbidden patterns.
    def __init__(self, max_input_length=500, max_iterations=10):

        self.max_input_length = max_input_length
        self.max_iterations = max_iterations

        # Patterns that should trigger a block (educational example).
        self.forbidden_patterns = ["rm -rf", "drop table", "delete all"]

    # Validate user input before it enters the loop.
    # Returns (is_valid: bool, reason: str)
    def validate_input(self, text):

        # Check length.
        if len(text) > self.max_input_length:
            return False, f"Input too long ({len(text)} > {self.max_input_length})"

        # Check for forbidden patterns (case-insensitive).
        lower = text.lower()
        for pattern in self.forbidden_patterns:

            if pattern in lower:
                return False, f"Blocked: contains forbidden pattern '{pattern}'"

        # All checks passed.
        return True, "OK"

    # Validate the LM's output before returning to the user.
    def validate_output(self, response):

        # Response must be a dict with expected keys.
        if not isinstance(response, dict):
            return False, "Response is not a dict"

        # Must have either content or tool_call (or both).
        if "content" not in response and "tool_call" not in response:
            return False, "Response missing 'content' and 'tool_call'"

        return True, "OK"

    # Check if we've exceeded the max iteration count for this turn.
    def check_iteration_limit(self, current_iteration):

        if current_iteration >= self.max_iterations:
            return False, f"Max iterations ({self.max_iterations}) reached"

        return True, "OK"

# Import time for sleep-based backoff (pure stdlib).
import time


# RecoveryHandler wraps risky operations with retry + fallback logic.
class RecoveryHandler:

    # Constructor — max_retries and base_delay control the retry policy.
    def __init__(self, max_retries=3, base_delay=0.1):
        self.max_retries = max_retries
        self.base_delay = base_delay  # seconds; kept tiny for a toy project
        self.failure_log = []  # records what went wrong

    # Execute a callable with retry logic.
    # `fn` is the function to attempt.
    # `fallback` is an optional default return if all retries fail.
    def execute(self, fn, fallback=None, context=""):

        # Loop up to max_retries times.
        for attempt in range(1, self.max_retries + 1):
            try:
                # Try calling the function.
                result = fn()
                return result
            except Exception as e:
                # Log the failure with attempt number and context.
                self.failure_log.append(
                    {"attempt": attempt, "error": str(e), "context": context}
                )
                # If this was the last attempt, break out.
                if attempt == self.max_retries:
                    break
                # Exponential backoff: delay doubles each retry.
                time.sleep(self.base_delay * (2 ** (attempt - 1)))

        # All retries exhausted — return fallback or raise.
        if fallback is not None:
            return fallback
        raise RuntimeError(
            f"All {self.max_retries} attempts failed for '{context}'. "
            f"Last error: {self.failure_log[-1]['error']}"
        )

    # Return the failure log (for debugging/monitoring).
    def get_failure_log(self):
        return list(self.failure_log)

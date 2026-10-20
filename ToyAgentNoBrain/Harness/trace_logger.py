# Line 1:  Import time for timestamps (pure stdlib).
import time


# Line 4:  ANSI escape codes — no external packages needed.
class _C:
    # Reset
    RESET = "\033[0m"
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    # Bold / light backgrounds
    BOLD = "\033[1m"
    BG_L_GREEN = "\033[102m"  # Light green background
    BG_L_RED = "\033[101m"  # Light red background
    BG_L_YELLOW = "\033[103m"  # Light yellow background


# Line 26:  Maps each component name to a foreground color for visual grouping.
_COMPONENT_COLORS = {
    "guardrails": _C.RED,
    "context": _C.CYAN,
    "lm": _C.MAGENTA,
    "tools": _C.YELLOW,
    "loop": _C.GREEN,
    "recovery": _C.BLUE,
}


# Line 35:  TraceLogger — records and prints every agent step with color.
class TraceLogger:

    # Line 38: Constructor.
    def __init__(self, verbose=True):
        self.entries = []
        self.verbose = verbose
        self._seq = 0

    # Line 42: Log a single event. Optionally prints it with color.
    def log(self, component, event, detail=""):
        self._seq += 1
        entry = {
            "seq": self._seq,
            "time": time.time(),
            "component": component,
            "event": event,
            "detail": detail,
        }
        self.entries.append(entry)

        # Line 52: If verbose, print the colored line to terminal.
        if self.verbose:
            print(self._format_line(entry))

    # Line 55: Build a single colored output line.
    def _format_line(self, entry):
        seq = entry["seq"]
        comp = entry["component"]
        event = entry["event"]
        detail = entry["detail"]

        # Line 61: Pick the component's color (default to white if unknown).
        comp_color = _COMPONENT_COLORS.get(comp, _C.WHITE)

        # Line 63: Build the detail segment with special-case coloring.
        detail_segment = self._color_detail(detail)

        # Line 65: Assemble the full line.
        line = (
            f"  [{seq:02d}] "  # sequence number (plain)
            f"{comp_color}{_C.BOLD}{comp:>14s}{_C.RESET} │ "  # component (colored, bold)
            f"{event:<25s} │ "  # event name (plain)
            f"{detail_segment}"  # detail (contextually colored)
        )
        return line

    # Line 73: Apply special coloring rules to the detail string.
    def _color_detail(self, detail):
        # Rule 1: "valid=True" → light green background + black foreground.
        if "valid=True" in detail:
            return f"{_C.BG_L_GREEN}{_C.BLACK}{detail}{_C.RESET}"

        # Rule 2: "valid=False" or "BLOCKED" → light red background + white foreground.
        if "valid=False" in detail or "BLOCKED" in detail:
            return f"{_C.BG_L_RED}{_C.WHITE}{detail}{_C.RESET}"

        # Rule 3: Contains an error keyword → yellow background + black foreground.
        if any(kw in detail.lower() for kw in ("error", "fail", "stopped")):
            return f"{_C.BG_L_YELLOW}{_C.BLACK}{detail}{_C.RESET}"

        # Default: no special coloring.
        return detail

    # Line 89: Print a summary report after the run completes.
    def report(self):
        print(f"\n{_C.BOLD}{'='*60}{_C.RESET}")
        print(f"{_C.BOLD}  TRACE REPORT — {len(self.entries)} events{_C.RESET}")
        print(f"{_C.BOLD}{'='*60}{_C.RESET}")
        for e in self.entries:
            comp_color = _COMPONENT_COLORS.get(e["component"], _C.WHITE)
            detail_seg = self._color_detail(e["detail"])
            print(
                f"  {e['seq']:02d} │ "
                f"{comp_color}{e['component']:<14s}{_C.RESET} │ "
                f"{e['event']:<25s} │ "
                f"{detail_seg}"
            )

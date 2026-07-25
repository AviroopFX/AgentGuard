"""
Policy Engine for AgentGuard.

Loads risk rules from rules.yaml and evaluates incoming ToolCall objects
against those rules to produce a PolicyResult (allow / flag / block / needs_approval).
"""

from pathlib import Path

import yaml

from agentguard.models import Decision, PolicyResult, RiskLevel, ToolCall


class PolicyEngine:
    """Evaluates tool calls against configurable risk rules."""

    def __init__(self, rules_path: str | None = None):
        if rules_path is None:
            # Default to rules.yaml sitting next to this file
            rules_path = Path(__file__).parent / "rules.yaml"

        with open(rules_path, "r") as f:
            config = yaml.safe_load(f)

        # Build a lookup: tool_name -> rule, so evaluation is fast (O(1) not O(n))
        self._rules_by_tool: dict[str, dict] = {
            rule["tool_name"]: rule for rule in config["rules"]
        }
        self._default_rule: dict = config["default"]

    def evaluate(self, tool_call: ToolCall) -> PolicyResult:
        """Evaluate a tool call and return a decision."""
        rule = self._rules_by_tool.get(tool_call.tool_name, self._default_rule)

        return PolicyResult(
            decision=Decision(rule["decision"]),
            risk_level=RiskLevel(rule["risk_level"]),
            reason=rule["reason"],
            tool_call=tool_call,
        )
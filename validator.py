"""
validator.py — Validation harness for AI agent outputs.

Each validator checks one rule and returns a ValidationResult.
The ValidationPipeline runs all validators and aggregates the results.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    message: str
    severity: str = "error"   # "error" | "warning" | "info"


@dataclass
class PipelineResult:
    task: str
    agent_output: Any
    results: List[ValidationResult] = field(default_factory=list)
    routed_to_human: bool = False

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "error")

    @property
    def summary(self) -> dict:
        return {
            "task": self.task,
            "overall_passed": self.passed,
            "routed_to_human": self.routed_to_human,
            "checks": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "message": r.message,
                    "severity": r.severity,
                }
                for r in self.results
            ],
        }


class ValidationPipeline:
    """
    Runs a list of validation rules against an agent's output.
    Applies supervised handoff routing when confidence is low.
    """

    CONFIDENCE_THRESHOLD = 0.7

    def __init__(self):
        self.validators: List[Callable] = [
            self._check_agent_succeeded,
            self._check_output_is_json,
            self._check_result_field_present,
            self._check_result_not_empty,
            self._check_confidence_field,
            self._check_confidence_above_threshold,
            self._check_latency_acceptable,
        ]

    def run(self, agent_response: dict) -> PipelineResult:
        output = agent_response.get("output")
        task = agent_response.get("task", "")

        pipeline_result = PipelineResult(task=task, agent_output=agent_response)

        for validator in self.validators:
            result = validator(agent_response)
            pipeline_result.results.append(result)

        # Supervised handoff: route to human if confidence is low or errors exist
        confidence = output.get("confidence") if isinstance(output, dict) else None
        if not pipeline_result.passed or (
            confidence is not None and confidence < self.CONFIDENCE_THRESHOLD
        ):
            pipeline_result.routed_to_human = True

        return pipeline_result

    # --- Individual validation rules ---

    def _check_agent_succeeded(self, resp: dict) -> ValidationResult:
        passed = resp.get("status") == "success"
        return ValidationResult(
            rule_name="agent_success",
            passed=passed,
            message="Agent ran successfully" if passed else f"Agent error: {resp.get('raw', '')}",
        )

    def _check_output_is_json(self, resp: dict) -> ValidationResult:
        passed = isinstance(resp.get("output"), dict)
        return ValidationResult(
            rule_name="output_is_json",
            passed=passed,
            message="Output is valid JSON" if passed else "Output could not be parsed as JSON",
        )

    def _check_result_field_present(self, resp: dict) -> ValidationResult:
        output = resp.get("output") or {}
        passed = isinstance(output, dict) and "result" in output
        return ValidationResult(
            rule_name="result_field_present",
            passed=passed,
            message="'result' field found in output" if passed else "Missing 'result' field in output",
        )

    def _check_result_not_empty(self, resp: dict) -> ValidationResult:
        output = resp.get("output") or {}
        result_value = output.get("result", "") if isinstance(output, dict) else ""
        passed = bool(str(result_value).strip())
        return ValidationResult(
            rule_name="result_not_empty",
            passed=passed,
            message="Result is non-empty" if passed else "Result field is empty",
        )

    def _check_confidence_field(self, resp: dict) -> ValidationResult:
        output = resp.get("output") or {}
        passed = isinstance(output, dict) and "confidence" in output
        return ValidationResult(
            rule_name="confidence_field_present",
            passed=passed,
            message="'confidence' field found" if passed else "Missing 'confidence' field",
            severity="warning",
        )

    def _check_confidence_above_threshold(self, resp: dict) -> ValidationResult:
        output = resp.get("output") or {}
        confidence = output.get("confidence") if isinstance(output, dict) else None
        if confidence is None:
            return ValidationResult(
                rule_name="confidence_threshold",
                passed=False,
                message="Cannot check threshold — confidence field missing",
                severity="warning",
            )
        passed = float(confidence) >= self.CONFIDENCE_THRESHOLD
        return ValidationResult(
            rule_name="confidence_threshold",
            passed=passed,
            message=f"Confidence {confidence:.2f} >= {self.CONFIDENCE_THRESHOLD}" if passed
                    else f"Confidence {confidence:.2f} below threshold {self.CONFIDENCE_THRESHOLD} → human review needed",
            severity="warning" if not passed else "info",
        )

    def _check_latency_acceptable(self, resp: dict) -> ValidationResult:
        latency = resp.get("latency_ms", 0)
        passed = latency < 10000  # 10 second max
        return ValidationResult(
            rule_name="latency_acceptable",
            passed=passed,
            message=f"Latency {latency}ms is acceptable" if passed else f"Latency {latency}ms exceeds 10s threshold",
            severity="warning",
        )

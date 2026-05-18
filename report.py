"""
report.py — Generates a readable evaluation report from run logs.
"""

from logger import load_all_logs


def generate_report() -> str:
    logs = load_all_logs()

    if not logs:
        return "No runs logged yet. Run main.py first."

    total = len(logs)
    passed = sum(1 for l in logs if l.get("validation", {}).get("overall_passed"))
    failed = total - passed
    human_routed = sum(1 for l in logs if l.get("validation", {}).get("routed_to_human"))

    avg_latency = (
        sum(l.get("latency_ms", 0) for l in logs) / total if total else 0
    )

    lines = [
        "=" * 58,
        "  AI AGENT EVALUATION REPORT",
        "=" * 58,
        f"  Total runs      : {total}",
        f"  Passed          : {passed}  ({100*passed//total if total else 0}%)",
        f"  Failed          : {failed}",
        f"  Routed to human : {human_routed}",
        f"  Avg latency     : {avg_latency:.0f}ms",
        "=" * 58,
        "",
    ]

    for i, log in enumerate(logs, 1):
        val = log.get("validation", {})
        status = "PASS" if val.get("overall_passed") else "FAIL"
        human = " [HUMAN REVIEW]" if val.get("routed_to_human") else ""
        lines.append(f"  Run {i:02d} | {status}{human}")
        lines.append(f"  Task    : {log.get('task', '')[:60]}")
        lines.append(f"  Latency : {log.get('latency_ms', 0)}ms")
        for check in val.get("checks", []):
            icon = "OK" if check["passed"] else "!!"
            lines.append(f"    [{icon}] {check['rule']}: {check['message']}")
        lines.append("")

    lines.append("=" * 58)
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())

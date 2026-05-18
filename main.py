"""
main.py — Entry point for the AI Agent Validation Pipeline.

Runs a set of test tasks through the agent, validates outputs,
logs every result, and prints a report summary.

Usage:
    python main.py
    python main.py --report      # show report from previous runs only
"""

import argparse
import sys
from colorama import Fore, Style, init

from agent import AIAgent
from validator import ValidationPipeline
from logger import log_run
from report import generate_report

init(autoreset=True)

# ── Test task suite ────────────────────────────────────────────────────────────
# Each entry is a dict with: task (str), description (str)
# Add or modify tasks here to test different scenarios.

TEST_TASKS = [
    {
        "task": "What is the capital of France? Reply in JSON with 'result' and 'confidence' keys.",
        "description": "Simple factual question",
    },
    {
        "task": "Summarize what an agentic AI workflow is in one sentence. Reply in JSON with 'result' and 'confidence' keys.",
        "description": "AI concept summary",
    },
    {
        "task": "List 3 best practices for building an AI evaluation pipeline. Reply in JSON with 'result' as a list and 'confidence' as a float.",
        "description": "Best practices list",
    },
    {
        "task": "What is 2 + 2? Reply in JSON with 'result' and 'confidence' keys.",
        "description": "Math sanity check",
    },
    {
        "task": "Explain what a validation harness is for AI systems in plain English. Reply in JSON with 'result' and 'confidence' keys.",
        "description": "Technical concept explanation",
    },
]


def run_pipeline(verbose: bool = True):
    agent = AIAgent()
    pipeline = ValidationPipeline()

    print(f"\n{Fore.CYAN}{'=' * 58}")
    print(f"  AI Agent Validation Pipeline")
    print(f"{'=' * 58}{Style.RESET_ALL}\n")

    for i, item in enumerate(TEST_TASKS, 1):
        task = item["task"]
        desc = item["description"]

        print(f"{Fore.YELLOW}[{i}/{len(TEST_TASKS)}] {desc}{Style.RESET_ALL}")
        print(f"  Task: {task[:70]}...")

        # 1. Run agent
        agent_response = agent.run(task)

        # 2. Validate output
        pipeline_result = pipeline.run(agent_response)

        # 3. Log result
        log_path = log_run(agent_response, pipeline_result.summary)

        # 4. Print result
        status_color = Fore.GREEN if pipeline_result.passed else Fore.RED
        status_label = "PASSED" if pipeline_result.passed else "FAILED"
        human_note = f"  {Fore.MAGENTA}→ Routed to human review{Style.RESET_ALL}" if pipeline_result.routed_to_human else ""

        print(f"  Status  : {status_color}{status_label}{Style.RESET_ALL}  |  Latency: {agent_response['latency_ms']}ms{human_note}")

        if verbose:
            for check in pipeline_result.results:
                icon = f"{Fore.GREEN}OK{Style.RESET_ALL}" if check.passed else f"{Fore.RED}!!{Style.RESET_ALL}"
                print(f"    [{icon}] {check.rule_name}: {check.message}")

        print(f"  Logged  : {log_path}")
        print()

    print(f"\n{Fore.CYAN}{'=' * 58}")
    print("  SUMMARY REPORT")
    print(f"{'=' * 58}{Style.RESET_ALL}\n")
    print(generate_report())


def main():
    parser = argparse.ArgumentParser(description="AI Agent Validation Pipeline")
    parser.add_argument("--report", action="store_true", help="Show report from previous runs only")
    args = parser.parse_args()

    if args.report:
        print(generate_report())
    else:
        run_pipeline()


if __name__ == "__main__":
    main()

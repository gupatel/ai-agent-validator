# AI Agent Validation Pipeline

A Python-based agentic workflow tool that runs tasks through an AI agent (Claude), validates outputs using a multi-rule validation harness, applies supervised handoff routing, and generates evaluation reports.

Built to demonstrate: agentic workflows, evaluation pipelines, validation harnesses, structured logging, and supervised handoff — core patterns in AI-native developer tooling.

---

## Features

- **AI Agent** — sends tasks to Claude API and returns structured JSON outputs
- **Validation Harness** — runs 7 rules against every agent output (schema, content, confidence, latency)
- **Supervised Handoff** — automatically routes low-confidence outputs to human review
- **Structured Logging** — every run is logged to JSON in `logs/`
- **Evaluation Report** — generates a readable summary across all runs with pass/fail rates

---

## Project Structure

```
ai_agent_validator/
├── agent.py          # AI agent — calls Claude API, returns structured output
├── validator.py      # Validation harness — 7 rules, pipeline runner, handoff routing
├── logger.py         # Structured JSON logger
├── report.py         # Evaluation report generator
├── main.py           # Entry point — runs full pipeline on test task suite
├── requirements.txt
└── logs/             # Auto-created; stores one JSON file per run
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-agent-validator.git
cd ai-agent-validator

# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here
```

Get a free API key at [console.anthropic.com](https://console.anthropic.com).

---

## Usage

```bash
# Run the full pipeline (5 test tasks)
python main.py

# Show report from previous runs only
python main.py --report
```

---

## Sample Output

```
==========================================================
  AI Agent Validation Pipeline
==========================================================

[1/5] Simple factual question
  Task: What is the capital of France?...
  Status  : PASSED  |  Latency: 842ms
    [OK] agent_success: Agent ran successfully
    [OK] output_is_json: Output is valid JSON
    [OK] result_field_present: 'result' field found in output
    [OK] result_not_empty: Result is non-empty
    [OK] confidence_field_present: 'confidence' field found
    [OK] confidence_threshold: Confidence 0.99 >= 0.7
    [OK] latency_acceptable: Latency 842ms is acceptable

[2/5] AI concept summary
  Status  : PASSED  |  Latency: 1203ms  → Routed to human review
  ...
```

---

## Validation Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `agent_success` | error | Agent API call completed without errors |
| `output_is_json` | error | Output is parseable as a JSON object |
| `result_field_present` | error | Output contains a `result` key |
| `result_not_empty` | error | Result value is non-empty |
| `confidence_field_present` | warning | Output contains a `confidence` key |
| `confidence_threshold` | warning | Confidence score is >= 0.7 |
| `latency_acceptable` | warning | Response time is under 10 seconds |

---

## Supervised Handoff Logic

Any run where:
- One or more error-level validations fail, **or**
- Confidence score is below `0.7`

...is flagged as `routed_to_human: true` in the log and marked in the report. This simulates a production safety net where uncertain agent outputs are reviewed before use.

---

## Extending the Project

- Add new validation rules in `validator.py` by adding a method prefixed with `_check_`
- Add new test tasks in the `TEST_TASKS` list in `main.py`
- Swap Claude for a different model by changing `model` in `agent.py`
- Connect a real human review queue by replacing the `routed_to_human` flag with an API call

---

## Tech Stack

- Python 3.12
- [Anthropic Python SDK](https://github.com/anthropic-sdk/anthropic-sdk-python)
- colorama (terminal output)

---

## Author

Built as a demonstration of agentic AI workflow patterns including validation harnesses, evaluation pipelines, and supervised handoff routing.

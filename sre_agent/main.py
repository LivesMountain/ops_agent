from __future__ import annotations

import argparse
import json

from .agent import build_sre_agent
from .config import Settings


def run_once(task: str) -> dict:
    settings = Settings()
    agent = build_sre_agent(settings)
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="SRE Agent CLI")
    parser.add_argument("task", help="incident or operation task description")
    args = parser.parse_args()

    result = run_once(args.task)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

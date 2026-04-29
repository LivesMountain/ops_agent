from __future__ import annotations

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .config import Settings
from .integrations import SREIntegrations
from .tools import build_tools


SRE_SYSTEM_PROMPT = """
You are an SRE on-call agent.

Goals:
1) Keep services reliable and quickly mitigate incidents.
2) Use tools for evidence-driven diagnosis (Kubernetes + Prometheus).
3) Integrate with ops ecosystem by creating Jira incidents and notifying Slack.
4) Before risky operations, explain impact and propose safer alternatives.
5) Return concise incident report: symptom, root-cause hypothesis, mitigation, next actions.
""".strip()


def build_sre_agent(settings: Settings):
    if settings.llm_provider != "openai":
        raise ValueError("Only openai provider is currently supported")

    model = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
    integrations = SREIntegrations(settings)
    tools = build_tools(integrations)

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SRE_SYSTEM_PROMPT,
    )

from __future__ import annotations

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from .integrations import IntegrationError, SREIntegrations


class KubectlInput(BaseModel):
    args: list[str] = Field(description="kubectl arguments, example: ['get','pods']")


class PrometheusInput(BaseModel):
    promql: str = Field(description="Prometheus query language expression")


class JiraInput(BaseModel):
    summary: str
    description: str
    project_key: str


class SlackInput(BaseModel):
    text: str
    channel: str | None = None


def build_tools(integrations: SREIntegrations) -> list[StructuredTool]:
    def _kubectl(args: list[str]) -> str:
        try:
            return integrations.run_kubectl(args)
        except IntegrationError as exc:
            return f"kubectl failed: {exc}"

    def _prometheus_query(promql: str) -> str:
        try:
            return integrations.query_prometheus(promql)
        except IntegrationError as exc:
            return f"prometheus query failed: {exc}"

    def _create_jira_incident(summary: str, description: str, project_key: str) -> str:
        try:
            return integrations.create_jira_incident(summary, description, project_key)
        except IntegrationError as exc:
            return f"jira incident creation failed: {exc}"

    def _send_slack_message(text: str, channel: str | None = None) -> str:
        try:
            return integrations.send_slack_message(text=text, channel=channel)
        except IntegrationError as exc:
            return f"slack send failed: {exc}"

    return [
        StructuredTool.from_function(
            func=_kubectl,
            name="kubectl",
            description="Run kubectl for cluster diagnostics and operational actions",
            args_schema=KubectlInput,
        ),
        StructuredTool.from_function(
            func=_prometheus_query,
            name="prometheus_query",
            description="Run PromQL query and return metrics result JSON",
            args_schema=PrometheusInput,
        ),
        StructuredTool.from_function(
            func=_create_jira_incident,
            name="create_jira_incident",
            description="Create incident ticket in Jira",
            args_schema=JiraInput,
        ),
        StructuredTool.from_function(
            func=_send_slack_message,
            name="send_slack_message",
            description="Send message to Slack channel",
            args_schema=SlackInput,
        ),
    ]

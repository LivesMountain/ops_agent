from __future__ import annotations

import json
import subprocess
from typing import Any

import httpx

from .config import Settings


class IntegrationError(RuntimeError):
    """Raised when external integration returns unexpected result."""


class SREIntegrations:
    """Ecosystem connectors for typical SRE workflows."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run_kubectl(self, args: list[str]) -> str:
        """Run kubectl command safely with fixed flags and timeout."""
        cmd = ["kubectl", *args, "-n", self.settings.kubernetes_namespace]
        try:
            proc = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=25,
            )
            return proc.stdout.strip() or "kubectl executed with no output"
        except subprocess.CalledProcessError as exc:
            raise IntegrationError(exc.stderr.strip() or str(exc)) from exc

    def query_prometheus(self, promql: str) -> str:
        if not self.settings.prometheus_base_url:
            raise IntegrationError("prometheus_base_url is not configured")

        url = f"{self.settings.prometheus_base_url.rstrip('/')}/api/v1/query"
        with httpx.Client(timeout=self.settings.webhook_timeout_seconds) as client:
            resp = client.get(url, params={"query": promql})
        if resp.status_code != 200:
            raise IntegrationError(f"Prometheus HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("status") != "success":
            raise IntegrationError(f"Prometheus query failed: {resp.text}")
        return json.dumps(data.get("data", {}), ensure_ascii=False, indent=2)

    def create_jira_incident(self, summary: str, description: str, project_key: str) -> str:
        if not (self.settings.jira_base_url and self.settings.jira_email and self.settings.jira_api_token):
            raise IntegrationError("Jira credentials are incomplete")

        api = f"{self.settings.jira_base_url.rstrip('/')}/rest/api/3/issue"
        payload: dict[str, Any] = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
                "issuetype": {"name": "Incident"},
            }
        }
        with httpx.Client(timeout=self.settings.webhook_timeout_seconds) as client:
            resp = client.post(api, auth=(self.settings.jira_email, self.settings.jira_api_token), json=payload)
        if resp.status_code not in (200, 201):
            raise IntegrationError(f"Jira HTTP {resp.status_code}: {resp.text}")
        return resp.text

    def send_slack_message(self, text: str, channel: str | None = None) -> str:
        if not self.settings.slack_bot_token:
            raise IntegrationError("slack_bot_token is not configured")
        target_channel = channel or self.settings.slack_channel
        if not target_channel:
            raise IntegrationError("Slack channel is not configured")

        api = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.settings.slack_bot_token}"}
        payload = {"channel": target_channel, "text": text}
        with httpx.Client(timeout=self.settings.webhook_timeout_seconds) as client:
            resp = client.post(api, headers=headers, json=payload)
        if resp.status_code != 200:
            raise IntegrationError(f"Slack HTTP {resp.status_code}: {resp.text}")
        return resp.text

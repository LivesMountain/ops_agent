# SRE Agent (LangChain 1.2.14)

一个基于 `langchain==1.2.14` 的运维/SRE 智能体示例，具备：

- **工具调用能力**：Kubernetes、Prometheus、Jira、Slack。
- **生态集成能力**：通过 API/CLI 与常见运维系统联动。
- **值班流程约束**：优先证据驱动诊断，输出标准化事故报告。

## 目录结构

- `sre_agent/config.py`：环境配置。
- `sre_agent/integrations.py`：各类外部系统连接器。
- `sre_agent/tools.py`：LangChain 工具定义。
- `sre_agent/agent.py`：Agent 组装。
- `sre_agent/main.py`：CLI 入口。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量示例

```bash
export OPENAI_API_KEY="..."
export LLM_MODEL="gpt-4.1-mini"

# 可选：运维生态
export PROMETHEUS_BASE_URL="http://prometheus.monitoring.svc:9090"
export KUBERNETES_NAMESPACE="default"

export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="..."

export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_CHANNEL="#ops-alert"
```

## 运行

```bash
python -m sre_agent.main "线上 API 5xx 激增，帮我排查并给出缓解方案"
```

## 能力示例

1. 通过 `prometheus_query` 检查错误率、延迟、流量。
2. 通过 `kubectl` 查看 Pod 状态与事件。
3. 自动生成 Jira Incident。
4. 将事故通告发送到 Slack。

## 说明

- 本仓库默认实现 OpenAI 模型提供方。
- 如需扩展（如飞书、PagerDuty、ServiceNow、CMDB），建议在 `integrations.py` 添加连接器，并在 `tools.py` 注册对应工具。

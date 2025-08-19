#!/bin/bash
export SECRET_KEY="test-secret-key"
export MCP_ENABLED_SERVICES="confluence,jira,slack"
export CONFLUENCE_BASE_URL="https://test.atlassian.net"
export CONFLUENCE_EMAIL="test@example.com"
export CONFLUENCE_API_TOKEN="test-token"
export JIRA_BASE_URL="https://test.atlassian.net"
export JIRA_EMAIL="test@example.com"
export JIRA_API_TOKEN="test-token"
export SLACK_BOT_TOKEN="xoxb-test-token"
export SLACK_SIGNING_SECRET="test-secret"

echo "✅ Environment variables set for testing"
echo "🧪 Running tests..."
uv run pytest tests/test_main.py -v
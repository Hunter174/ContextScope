import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from core.tools.tool_decorator import register_tool

load_dotenv()

BASE_URL = os.getenv("ATLASSIAN_BASE_URL")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
TOKEN = os.getenv("ATLASSIAN_TOKEN")
PROJECT_KEY = os.getenv("ATLASSIAN_PROJECT_KEY", "PROJ")


@register_tool(
    name="create_jira_issue",
    domain="atlassian",
    level="composite"
)
def create_issue(summary: str, description: str, issue_type: str = "Task"):
    """
    Create a new Jira issue in the configured Atlassian project.

    This function sends a POST request to the Jira REST API to create an issue
    using the provided summary, description, and issue type. The description is
    formatted using Atlassian Document Format (ADF).

    Args:
        summary (str): Short title of the issue.
        description (str): Detailed description of the issue (plain text).
        issue_type (str, optional): Jira issue type (e.g., "Task", "Bug", "Story").
            Defaults to "Task".

    Returns:
        dict:
            On success:
                {
                    "issue_key": str,   # e.g., "PROJ-123"
                    "issue_url": str    # direct URL to the issue in Jira
                }
            On failure:
                {
                    "error": str        # error message from API or config validation
                }

    Notes:
        - Requires environment variables: ATLASSIAN_BASE_URL, ATLASSIAN_EMAIL, ATLASSIAN_TOKEN.
        - Uses HTTP Basic Auth with API token.
        - PROJECT_KEY defaults to "PROJ" if not provided.
    """
    if not all([BASE_URL, EMAIL, TOKEN]):
        return {"error": "Missing Atlassian configuration"}

    url = f"{BASE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": {"name": issue_type},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": description}
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        auth=HTTPBasicAuth(EMAIL, TOKEN),
    )

    if response.status_code >= 400:
        return {"error": response.text}

    data = response.json()
    return {
        "issue_key": data.get("key"),
        "issue_url": f"{BASE_URL}/browse/{data.get('key')}"
    }


@register_tool(
    name="get_jira_issue",
    domain="atlassian",
    level="atomic"
)
def get_issue(issue_key: str):
    """
    Retrieve basic details for a specific Jira issue.

    This function queries the Jira REST API for a single issue and returns
    a minimal subset of fields useful for quick inspection.

    Args:
        issue_key (str): Unique Jira issue identifier (e.g., "PROJ-123").

    Returns:
        dict:
            On success:
                {
                    "key": str,         # issue key
                    "summary": str,     # issue title
                    "status": str       # current workflow status (e.g., "To Do", "Done")
                }
            On failure:
                {
                    "error": str        # error message from API
                }

    Notes:
        - Requires valid Atlassian credentials via environment variables.
        - Only a subset of fields is returned; extend if more detail is needed.
    """
    url = f"{BASE_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, TOKEN)
    )

    if response.status_code >= 400:
        return {"error": response.text}

    data = response.json()
    return {
        "key": data["key"],
        "summary": data["fields"]["summary"],
        "status": data["fields"]["status"]["name"]
    }


@register_tool(
    name="search_jira_issues",
    domain="atlassian",
    level="composite"
)
def get_issues(jql: str):
    """
    Search for Jira issues using a JQL (Jira Query Language) expression.

    This function executes a search query against the Jira REST API and
    returns a simplified list of matching issues.

    Args:
        jql (str): Jira Query Language string (e.g., "project = PROJ AND status = 'To Do'").

    Returns:
        dict:
            On success:
                {
                    "issues": [
                        {
                            "key": str,         # issue key
                            "summary": str      # issue title
                        },
                        ...
                    ]
                }
            On failure:
                {
                    "error": str              # error message from API
                }

    Notes:
        - Results are limited by Jira's default pagination unless extended.
        - Only key and summary are returned; additional fields require modification.
        - Requires valid Atlassian credentials via environment variables.
    """
    url = f"{BASE_URL}/rest/api/3/search"

    response = requests.get(
        url,
        params={"jql": jql},
        auth=HTTPBasicAuth(EMAIL, TOKEN)
    )

    if response.status_code >= 400:
        return {"error": response.text}

    data = response.json()

    issues = [
        {
            "key": i["key"],
            "summary": i["fields"]["summary"]
        }
        for i in data.get("issues", [])
    ]

    return {"issues": issues}
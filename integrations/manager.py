from integrations.ollama import OllamaIntegration
from integrations.aws_textract import AWSTextractIntegration
from integrations.jira import JiraIntegration

class IntegrationManager:

    def __init__(self):

        self.integrations = [
            OllamaIntegration(),
            AWSTextractIntegration(),
            JiraIntegration(),
        ]

    def get_supported_integrations(self):
        return self.integrations
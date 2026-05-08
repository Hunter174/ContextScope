from integrations.base import BaseIntegration


class JiraIntegration(BaseIntegration):
    name = "jira"
    secret_fields = ["token"]

    def setup(self):
        self.email = input("Atlassian Email: ")
        self.base_url = input("Atlassian Base URL: ")
        self.project_key = input("Atlassian Project Key: ")
        self.token = input("Atlassian API Token: ")

    def validate(self):
        return True

    def export_config(self):
        return {
            "base_url": self.base_url,
            "project_key": self.project_key,
            "email": self.email,
        }

    def export_secrets(self):
        return {"token": self.token}
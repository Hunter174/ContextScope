from integrations.base import BaseIntegration


class AWSTextractIntegration(BaseIntegration):

    name = "aws_textract"

    secret_fields = [
        "access_key",
        "secret_key"
    ]

    def setup(self):

        self.access_key = input(
            "AWS Access Key: "
        )

        self.secret_key = input(
            "AWS Secret Key: "
        )

        self.region = input(
            "AWS Region [us-east-1]: "
        ) or "us-east-1"

    def validate(self):

        return True

    def export_config(self):

        return {
            "region": self.region
        }

    def export_secrets(self):

        return {
            "access_key": self.access_key,
            "secret_key": self.secret_key
        }

from abc import ABC, abstractmethod


class BaseIntegration(ABC):

    name = "base"

    required = False

    secret_fields = []

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    def export_config(self):
        return {}

    def export_secrets(self):
        return {}

    def secret_keys(self):

        return self.secret_fields
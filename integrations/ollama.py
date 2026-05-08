from integrations.base import BaseIntegration


class OllamaIntegration(BaseIntegration):

    name = "ollama"

    required = True

    SUPPORTED_MODELS = [
        "gemma4:31b-cloud",
        "llama3.3",
        "qwen3"
    ]

    def setup(self):

        print("\nSelect model:\n")

        for i, model in enumerate(
            self.SUPPORTED_MODELS
        ):

            print(
                f"{i + 1}. {model}"
            )

        idx = int(input("\n> ")) - 1

        self.model = (
            self.SUPPORTED_MODELS[idx]
        )

    def validate(self):

        return True

    def export_config(self):

        return {
            "model": self.model
        }

    def export_secrets(self):
        return {}
